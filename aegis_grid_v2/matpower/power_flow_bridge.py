"""
AEGIS-Grid MATPOWER Cyber-Physical Bridge

Extracts:
  V  : bus voltage magnitudes
  Va : bus voltage angles
  I  : branch currents
  Y  : bus admittance matrix
  L  : Laplacian matrix derived from |Y|
"""

import numpy as np
import subprocess
import re


class MatpowerBridge:

    def __init__(self):
        pass


    def run_case(self, case="case9"):

        script = f"""
        define_constants;
        mpc = loadcase('{case}');
        results = runpf(mpc);

        if results.success
            disp('PF_SUCCESS');
            V = results.bus(:,8);
            Va = results.bus(:,9);
            fprintf('VOLTAGES: ');
            fprintf('%.6f ', V);
            fprintf('\\n');

            fprintf('ANGLES: ');
            fprintf('%.6f ', Va);
            fprintf('\\n');
        else
            disp('PF_FAILED');
        end
        """

        cmd = ["octave", "--quiet", "--eval", script]

        result = subprocess.run(cmd, capture_output=True, text=True)

        output = result.stdout + result.stderr

        voltages = []
        angles = []

        v_match = re.search(r"VOLTAGES:\s*([\d\.\s\-]+)", output)
        a_match = re.search(r"ANGLES:\s*([\d\.\s\-]+)", output)

        if v_match:
            voltages = [float(x) for x in v_match.group(1).split()]

        if a_match:
            angles = [float(x) for x in a_match.group(1).split()]

        return {
            "voltages": voltages,
            "angles": angles,
            "success": "PF_SUCCESS" in output
        }


    def laplacian_from_admittance(self, Y):

        D = np.diag(np.sum(np.abs(Y), axis=1))

        return D - np.abs(Y)
