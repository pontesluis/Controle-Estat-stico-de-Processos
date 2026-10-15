import unittest
from pathlib import Path
from cep.io_json import read_and_validate_json
from cep.modes import run_calibration
from cep.prob import prob_normal, prob_binomial_eq, prob_binomial_leq, beta_shift_xbar

class TestSPCBase(unittest.TestCase):
    def setUp(self):
        self.json_path = Path("exemplos/dados_calibracao_x.json")
        self.data = read_and_validate_json(self.json_path)

    def test_valida_iteracao_0_e_final(self):
        res = run_calibration(self.data, allow_revision=True)
        iter0 = res["iterations"][0]
        
        # Testar Iteração 0
        self.assertAlmostEqual(iter0["x_double_bar"], 4.960650, places=4)
        self.assertAlmostEqual(iter0["r_bar"], 0.021950, places=4)
        self.assertAlmostEqual(iter0["sigma_hat"], 0.009437, places=4)
        
        self.assertAlmostEqual(iter0["lic_x"], 4.947985, places=4)
        self.assertAlmostEqual(iter0["lc_x"], 4.960650, places=4)
        self.assertAlmostEqual(iter0["lsc_x"], 4.973315, places=4)
        
        # Violadores na Iteração 0 (0-based)
        # Amostra 2 = índice 1; Amostra 9 = índice 8; Amostra 17 = índice 16
        self.assertTrue(1 in iter0["violators"])
        self.assertTrue(8 in iter0["violators"])
        self.assertTrue(16 in iter0["violators"])

        # Revisão Final
        fl = res["final_limits"]
        self.assertAlmostEqual(fl["x_double_bar"], 4.961235, places=4)
        self.assertAlmostEqual(fl["r_bar"], 0.020118, places=4)
        self.assertAlmostEqual(fl["sigma_hat"], 0.008649, places=4)

        self.assertAlmostEqual(fl["lic_x"], 4.949627, places=4)
        self.assertAlmostEqual(fl["lc_x"], 4.961235, places=4)
        self.assertAlmostEqual(fl["lsc_x"], 4.972843, places=4)

    def test_probabilidades(self):
        # N(mu, sigma) - verificação pedida P(Z<1.96) = 0.9750
        p_196 = prob_normal(0, 1, b=1.96)
        self.assertAlmostEqual(p_196, 0.9750, places=4)
        
        # phi(3) - phi(-3) = 0.9973
        p_3 = prob_normal(0, 1, a=-3, b=3)
        self.assertAlmostEqual(p_3, 0.9973, places=4)
        
        # B(n=10, p=0.1)
        self.assertAlmostEqual(prob_binomial_eq(10, 0, 0.1), 0.3487, places=4)
        self.assertAlmostEqual(prob_binomial_eq(10, 1, 0.1), 0.3874, places=4)
        self.assertAlmostEqual(prob_binomial_eq(10, 2, 0.1), 0.1937, places=4)
        self.assertAlmostEqual(prob_binomial_leq(10, 1, 0.1), 0.7361, places=4)
        
    def test_deslocamento(self):
        # Deslocamento n=5, delta=1.0 -> beta=0.7775, pd=0.2225, arl1=4.50
        beta = beta_shift_xbar(1.0, 5)
        self.assertAlmostEqual(beta, 0.7775, places=4)
        self.assertAlmostEqual(1.0 - beta, 0.2225, places=4)
        self.assertAlmostEqual(1.0 / (1.0 - beta), 4.50, places=2)