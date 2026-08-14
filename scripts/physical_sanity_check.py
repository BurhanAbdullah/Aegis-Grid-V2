#!/usr/bin/env python3
import os, sys
import numpy as np

sys.path.insert(0, os.path.abspath("."))
from core.grid_topology import get_ieee_case_data, build_ybus, compute_h_x

def run_physical_audit():
    cases = ["case9", "case14", "case30", "case118"]
    results = {}
    
    print("=" * 80)
    print("INDEPENDENT PHYSICAL MODEL SANITY CHECK: POWER CONSERVATION AUDIT")
    print("=" * 80)
    
    for case in cases:
        cd = get_ieee_case_data(case)
        N = cd["num_buses"]
        baseMVA = cd["baseMVA"]
        Ybus, G, B = build_ybus(cd)
        
        # Nominal flat voltage vector V_i = 1.0 < 0.0 deg
        Vm = np.array([b[2] for b in cd["buses"]])
        Va = np.array([np.radians(b[3]) for b in cd["buses"]])
        V = Vm * np.exp(1j * Va)
        
        # 1. Compute node currents I = Ybus * V
        I = Ybus @ V
        
        # 2. Compute apparent power S_i = V_i * conj(I_i)
        S = V * np.conj(I)
        P_calc = np.real(S)
        Q_calc = np.imag(S)
        
        sum_P_inj = np.sum(P_calc)
        sum_Q_inj = np.sum(Q_calc)
        
        # Declared load quantities Pd, Qd
        Pd = np.array([b[4] for b in cd["buses"]])
        Qd = np.array([b[5] for b in cd["buses"]])
        sum_Pd = np.sum(Pd)
        sum_Qd = np.sum(Qd)
        
        # Measurement vector h(x) output at nominal state
        x_nominal = np.zeros(2 * N - 1)
        x_nominal[N - 1:] = 1.0
        h_x = compute_h_x(x_nominal, G, B)
        h_V = h_x[:N]
        h_P = h_x[N:2*N]
        h_Q = h_x[2*N:]
        
        # Compare h(x) P and Q with P_calc and Q_calc
        p_h_diff = np.max(np.abs(h_P - P_calc))
        q_h_diff = np.max(np.abs(h_Q - Q_calc))
        
        # Compute branch losses
        branch_losses_P = 0.0
        branch_losses_Q = 0.0
        for branch in cd["branches"]:
            f = int(branch[0]) - 1
            t = int(branch[1]) - 1
            r = branch[2]
            x = branch[3]
            b_sh = branch[4]
            z = complex(r, x)
            if abs(z) > 1e-9:
                y = 1.0 / z
                i_ft = (V[f] - V[t]) * y
                branch_losses_P += np.real(i_ft * np.conj(i_ft) * z)
                branch_losses_Q += np.imag(i_ft * np.conj(i_ft) * z) - 0.5 * b_sh * (abs(V[f])**2 + abs(V[t])**2)
                
        abs_p_err = abs(sum_P_inj - branch_losses_P)
        abs_q_err = abs(sum_Q_inj - branch_losses_Q)
        rel_p_err = (abs_p_err / (sum_Pd + 1e-9)) * 100.0 if sum_Pd > 0 else 0.0
        rel_q_err = (abs_q_err / (sum_Qd + 1e-9)) * 100.0 if sum_Qd > 0 else 0.0
        
        print(f"\nCASE: {case} (Buses={N}, Branches={cd['num_branches']})")
        print(f"  Voltage vector min/max : {np.min(np.abs(V)):.4f} / {np.max(np.abs(V)):.4f} p.u.")
        print(f"  Sum P_injected         : {sum_P_inj:.6f} p.u. ({sum_P_inj * baseMVA:.3f} MW)")
        print(f"  Sum Q_injected         : {sum_Q_inj:.6f} p.u. ({sum_Q_inj * baseMVA:.3f} MVAr)")
        print(f"  Sum Branch P Losses    : {branch_losses_P:.6f} p.u. ({branch_losses_P * baseMVA:.3f} MW)")
        print(f"  Sum Branch Q Losses    : {branch_losses_Q:.6f} p.u. ({branch_losses_Q * baseMVA:.3f} MVAr)")
        print(f"  Sum Active Load Pd     : {sum_Pd:.6f} p.u. ({sum_Pd * baseMVA:.3f} MW)")
        print(f"  Sum Reactive Load Qd   : {sum_Qd:.6f} p.u. ({sum_Qd * baseMVA:.3f} MVAr)")
        print(f"  h(x) Consistency       : Max P diff = {p_h_diff:.2e}, Max Q diff = {q_h_diff:.2e}")
        print(f"  Conservation Discrepancy (P_inj - P_loss): Abs = {abs_p_err:.6e} p.u. | Rel = {rel_p_err:.4f}%")
        print(f"  Conservation Discrepancy (Q_inj - Q_loss): Abs = {abs_q_err:.6e} p.u. | Rel = {rel_q_err:.4f}%")
        
        results[case] = {
            "N": N,
            "sum_P_inj": sum_P_inj,
            "sum_Q_inj": sum_Q_inj,
            "sum_Pd": sum_Pd,
            "sum_Qd": sum_Qd,
            "p_h_diff": p_h_diff,
            "q_h_diff": q_h_diff,
            "abs_p_err": abs_p_err,
            "abs_q_err": abs_q_err,
            "rel_p_err": rel_p_err,
            "rel_q_err": rel_q_err
        }

    print("\n" + "=" * 80)
    print("PHYSICAL MODEL SANITY CHECK SUMMARY")
    print("=" * 80)
    for c, r in results.items():
        pass_fail = "PASS" if r["p_h_diff"] < 1e-12 and r["q_h_diff"] < 1e-12 and r["abs_p_err"] < 1e-10 else "FAIL"
        print(f"Case {c:7s} | h(x) Match: {r['p_h_diff'] < 1e-12} | Abs P Loss Err: {r['abs_p_err']:.2e} | Result: {pass_fail}")

if __name__ == "__main__":
    run_physical_audit()
