import numpy as np
import yoloapnea.evaluate as evaluate
from sklearn.metrics import f1_score
from unittest import TestCase
from yoloapnea.apneas import ApneaType


class TestEvaluate(TestCase):

    def setUp(self):
        self.apnea_types = [ApneaType.Obstructive]
        self.pred = np.array([0, 0.3, 0, 0, 0, 0.3, 1, 0])
        self.truth = np.array([1, 1, 0, 0, 0, 1, 0, 0])
        self.evaluate = evaluate.Evaluate(self.pred, self.truth, self.apnea_types, 0)

    def test_f1(self):
        value = self.evaluate.f1
        self.assertEqual(value, f1_score(y_true=self.truth, y_pred=self.pred > 0))

    def test_init(self):
        apnea_types = self.apnea_types
        pred = np.array([1, 1, 1])
        truth = np.array([0, 1, 0])
        pred_one_full_event = evaluate.Evaluate(pred, truth, apnea_types, 0)
        pred_one_full_event.ahi

        truth_one_full_event = evaluate.Evaluate(truth, pred, apnea_types, 0)
        truth_one_full_event.ahi

        pred_starts_with_event = evaluate.Evaluate(np.array([1, 0, 0]), truth, apnea_types, 0)
        pred_starts_with_event.ahi

        pred_starts_and_ends_with_event = evaluate.Evaluate(np.array([0.5, 0, 1]), truth, apnea_types, 0)
        pred_starts_and_ends_with_event.ahi

        pred_starts_and_ends_with_event_with_confidence = evaluate.Evaluate(np.array([0.5, 0, 1]), truth, apnea_types,
                                                                            0)
        pred_starts_and_ends_with_event_with_confidence.ahi

        longer_pred = evaluate.Evaluate(np.array([0.5, 1, 1, 0, 0, 0.4, 0.1, 0, 1]),
                                        np.array([0, 0, 1, 0, 1, 1, 0.1, 1, 1]), apnea_types, 0)
        longer_pred.ahi

    def test_predictedAHI(self):
        value = self.evaluate.predictionAHI
        self.assertGreaterEqual(value, 0)

    def test_groundTruth_AHI(self):
        value = self.evaluate.groundTruthAHI
        self.assertGreaterEqual(value, 0)

    def test_scores(self):
        scores = self.evaluate.scores
        print(scores)

    def test_tp_apneas(self):
        one_tp = evaluate.Evaluate(np.array([0, 1, 0]), [0, 1, 0], self.apnea_types, 0)
        print(one_tp.tp_apneas)
        self.assertEqual(one_tp.tp_apneas, 1)

        # two_tp = evaluate.Evaluate(np.array([0, 1, 0,0,1]),[0, 1, 0,0,1], self.apnea_types, 0)
        # print(two_tp.tp_apneas)
        # self.assertEqual(two_tp.tp_apneas,2)

    def test_fp_apneas(self):
        no_fp = evaluate.Evaluate(np.array([0, 1, 0]), [0, 1, 0], self.apnea_types, 0)
        self.assertEqual(no_fp.fp_apneas, 0)

        one_fp = evaluate.Evaluate(np.array([0, 1, 0]), [0, 0, 1], self.apnea_types, 0)
        self.assertEqual(one_fp.fp_apneas, 1)

        two_fp = evaluate.Evaluate(np.array([1, 0, 1]), [0, 1, 0], self.apnea_types, 0)
        self.assertEqual(two_fp.fp_apneas, 2)

        no_fp = evaluate.Evaluate(np.array([1, 1, 1, 0, 0, 0, 1, 1, 1, 1]) \
                                  , [0, 1, 0, 0, 0, 1, 1, 1, 0, 1], self.apnea_types, 0)
        self.assertEqual(no_fp.fp_apneas, 0)

        two_fp = evaluate.Evaluate(np.array([1, 1, 1, 0, 0, 0, 1, 0, 1, 1]) \
                                   , [0, 0, 0, 1, 0, 1, 1, 1, 0, 0], self.apnea_types, 0)
        self.assertEqual(two_fp.fp_apneas, 2)

    def test_fn_apneas(self):
        no_fn = evaluate.Evaluate(np.array([0, 1, 0]), [0, 1, 1], self.apnea_types, 0)
        self.assertEqual(no_fn.fn_apneas, 0)

        one_fn = evaluate.Evaluate(np.array([0, 1, 0]), [0, 0, 1], self.apnea_types, 0)
        self.assertEqual(one_fn.fn_apneas, 1)

        one_fn = evaluate.Evaluate(np.array([1, 1, 1, 0, 0, 0, 1, 0, 1, 1]) \
                                   , [0, 0, 0, 1, 0, 1, 1, 1, 0, 0], self.apnea_types, 0)
        self.assertEqual(one_fn.fn_apneas, 1)
