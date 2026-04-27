"""
Bridge between MATPOWER case files and AEGIS-Grid residual detector.

Calls MATPOWER via oct2py or matlab.engine to get:
  - V  : bus voltage vector
  - I  : branch current vector  
  - J  : power flow Jacobian (from t_jacobian test structure)
  - L  : graph Laplacian from admittance matrix
"""
