"""Deliberately contaminated fixtures for the temporal / leakage rules. Run:
    python -I pilot/stackexchange_raw/tests/test_temporal.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import temporal as T  # noqa: E402

Q = dict(id=1, owner=10, created="2020-01-01T10:00:00.000", title="wifi drops")
BODY0 = "<p>My wifi connection drops every few minutes on Ubuntu 20.04 laptop.</p>"
ANS_TEXT = ("Disable power management for the wifi card by running sudo iw dev wlan0 set power_save off "
            "and then edit the file /etc/NetworkManager/conf.d/default-wifi-powersave-on.conf setting wifi.powersave = 2")


def hist(extra=()):
    h = [dict(type=T.H_INIT_BODY, created="2020-01-01T10:00:00.000", user=10, text=BODY0, revision_guid="r0")]
    h += list(extra)
    return h


def ans(created, aid=100, body=None):
    return dict(id=aid, created=created, body=body or "<p>%s</p>" % ANS_TEXT)


def edit(created, text, user=10, guid="r1"):
    return dict(type=T.H_EDIT_BODY, created=created, user=user, text=text, revision_guid=guid)


def comment(cid, created, text, user=10):
    return dict(id=cid, created=created, text=text, user=user)


NEW_FACT = ("Here is the output of dmesg: iwlwifi 0000:02:00.0 firmware error reset happens after lid "
            "suspend and the signal strength shows -80 dBm in iwconfig output")


class TestTemporal(unittest.TestCase):
    def run_it(self, history, comments, answers, accepted=100):
        return T.build_thread_states(Q, history, comments, answers, accepted)

    def test_two_real_states(self):
        r = self.run_it(hist(), [comment(5, "2020-01-01T10:30:00.000", NEW_FACT)], [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 2)
        self.assertIn("dmesg", r["later_text"])
        self.assertNotIn("dmesg", r["early_text"])

    def test_late_added_diagnosis_after_first_answer_is_excluded(self):
        r = self.run_it(hist(), [comment(5, "2020-01-01T13:00:00.000", NEW_FACT)], [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 1)

    def test_answer_before_clarification_not_counted(self):
        r = self.run_it(hist([edit("2020-01-01T12:05:00.000", BODY0 + "\n" + NEW_FACT)]), [],
                        [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 1)

    def test_accepted_answer_after_first_answer_uses_first_answer_cutoff(self):
        answers = [ans("2020-01-01T11:00:00.000", aid=99, body="<p>try rebooting</p>"),
                   ans("2020-01-01T14:00:00.000", aid=100)]
        r = self.run_it(hist(), [comment(5, "2020-01-01T12:00:00.000", NEW_FACT)], answers)
        self.assertEqual(r["cutoff_reason"], "first_answer")
        self.assertEqual(r["n_states"], 1)  # comment is after FIRST answer (11:00), though before accepted

    def test_solution_in_comment_moves_cutoff_earlier_and_flags(self):
        sol = "just run sudo iw dev wlan0 set power_save off then edit /etc/NetworkManager/conf.d/default-wifi-powersave-on.conf"
        cs = [comment(4, "2020-01-01T10:10:00.000", sol, user=77),
              comment(5, "2020-01-01T10:30:00.000", NEW_FACT)]
        r = self.run_it(hist(), cs, [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["cutoff_reason"], "comment_discloses_solution")
        self.assertEqual(r["leakage"], "suspected")
        self.assertEqual(r["n_states"], 1)

    def test_reversed_timestamps_edit_before_question_rejected(self):
        r = self.run_it(hist([edit("2019-12-31T10:00:00.000", BODY0 + NEW_FACT)]), [], [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 1)

    def test_missing_history_abstains(self):
        r = self.run_it([], [], [ans("2020-01-01T12:00:00.000")])
        self.assertIn("no_initial_body_in_history", r["reasons"])
        self.assertEqual(r["n_states"], 0)

    def test_user_quoting_solution_text_rejected(self):
        quote = "I read online that I should " + ANS_TEXT
        r = self.run_it(hist(), [comment(5, "2020-01-01T10:30:00.000", quote)], [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 1)
        self.assertEqual(r["leakage"], "suspected")

    def test_resolution_claim_rejected(self):
        r = self.run_it(hist(), [comment(5, "2020-01-01T10:30:00.000",
                                         "Thanks everyone that worked and the problem is solved now after I toggled the setting in the router page")],
                        [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 1)

    def test_late_edit_masquerading_as_original(self):
        # an edit stamped AFTER the cutoff must not be used to define the early text
        r = self.run_it(hist([edit("2020-01-01T13:00:00.000", BODY0 + "\n" + NEW_FACT)]), [],
                        [ans("2020-01-01T12:00:00.000")])
        self.assertNotIn("dmesg", r["early_text"])

    def test_equal_timestamp_abstains(self):
        r = self.run_it(hist(), [comment(5, "2020-01-01T12:00:00.000", NEW_FACT)], [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 1)
        self.assertTrue(any(why == "equal_timestamp_abstain" for _, why in r["rejected"]))

    def test_non_owner_comment_is_not_symptom(self):
        r = self.run_it(hist(), [comment(5, "2020-01-01T10:30:00.000", NEW_FACT, user=99)], [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 1)

    def test_formatting_only_edit_not_new_fact(self):
        r = self.run_it(hist([edit("2020-01-01T10:20:00.000", BODY0.replace("<p>", "<p> ").replace("</p>", " </p>"))]), [],
                        [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 1)

    def test_thanks_comment_not_new_fact(self):
        r = self.run_it(hist(), [comment(5, "2020-01-01T10:30:00.000", "Thanks")], [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 1)

    def test_accepted_missing_abstains(self):
        r = self.run_it(hist(), [], [ans("2020-01-01T12:00:00.000", aid=5)], accepted=100)
        self.assertIn("accepted_answer_not_in_dump", r["reasons"])

    def test_malformed_comment_timestamp_rejected(self):
        r = self.run_it(hist(), [comment(5, "garbage", NEW_FACT)], [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 1)

    def test_request_for_clarification_is_not_observation(self):
        r = self.run_it(hist(), [comment(5, "2020-01-01T10:30:00.000",
                        "Thanks. I am pretty new to linux so can you please elaborate a little on what you mean by that suggestion earlier")],
                        [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 1)

    def test_solve_the_problem_claim_rejected(self):
        r = self.run_it(hist(), [comment(5, "2020-01-01T10:30:00.000",
                        "Both driver versions 340.102 and 304.135 solve the problem for me, tested after waiting for the screen to blank")],
                        [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 1)

    def test_username_digits_do_not_count_as_facts(self):
        r = self.run_it(hist(), [comment(5, "2020-01-01T10:30:00.000",
                        "@aking1012: Thanks. I am pretty new to linux so can you please elaborate a little on what you mean by that")],
                        [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 1)

    def test_three_states(self):
        f2 = ("Also the problem occurs only on battery power and journalctl shows NetworkManager deauthenticating "
              "from the access point with reason code 3 around the same time")
        r = self.run_it(hist(), [comment(5, "2020-01-01T10:30:00.000", NEW_FACT),
                                 comment(6, "2020-01-01T11:00:00.000", f2)], [ans("2020-01-01T12:00:00.000")])
        self.assertEqual(r["n_states"], 3)
        self.assertIsNotNone(r["advanced_text"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
