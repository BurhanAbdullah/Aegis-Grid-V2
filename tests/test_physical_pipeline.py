import unittest
import numpy as np

from core.physical_data_pipeline import load_canonical_case, solved_case, generate_sample


class PhysicalPipelineTests(unittest.TestCase):
    def test_canonical_dimensions(self):
        expected = {"case9": (9, 9), "case14": (14, 20), "case30": (30, 41), "case118": (118, 186)}
        for name, (nbus, nbranch) in expected.items():
            ppc = load_canonical_case(name)
            self.assertEqual(ppc["bus"].shape[0], nbus)
            self.assertEqual(ppc["branch"].shape[0], nbranch)

    def test_canonical_newton_power_flow(self):
        for name in ("case9", "case14", "case30", "case118"):
            result, x, ybus = solved_case(name)
            self.assertEqual(len(x), 2 * result["bus"].shape[0] - 1)
            self.assertEqual(ybus.shape, (result["bus"].shape[0], result["bus"].shape[0]))
            self.assertTrue(np.all(np.isfinite(result["bus"][:, 7])))
            self.assertTrue(np.all(result["bus"][:, 7] > 0.80))
            self.assertTrue(np.all(result["bus"][:, 7] < 1.20))

    def test_measurement_dimensions_and_finite_values(self):
        for name in ("case9", "case14"):
            z, dt, meta = generate_sample(name, "baseline", "Tier 0 (Benign)", 0, np.random.RandomState(42))
            self.assertEqual(z.size, 3 * load_canonical_case(name)["bus"].shape[0])
            self.assertGreater(dt, 0.0)
            self.assertTrue(np.all(np.isfinite(z)))
            self.assertEqual(meta["attack_mode"], "none")

    def test_fdia_is_generated_from_jacobian(self):
        # Reproducibility plus nonzero attack magnitude verifies the canonical FDIA path executes.
        for name in ("case9", "case14"):
            z1, _, m1 = generate_sample(name, "fdia", "Tier 2 (Moderate)", 3, np.random.RandomState(7))
            z2, _, m2 = generate_sample(name, "fdia", "Tier 2 (Moderate)", 3, np.random.RandomState(7))
            np.testing.assert_allclose(z1, z2)
            self.assertEqual(m1["attack_mode"], "jacobian_fdia")
            self.assertGreater(m1["attack_magnitude"], 0.0)
            self.assertEqual(m1, m2)


if __name__ == "__main__":
    unittest.main()
