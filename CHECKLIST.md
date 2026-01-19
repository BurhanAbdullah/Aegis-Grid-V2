# Repository Interpretation Checklist

This repository is a frozen research archive. It is not intended for active
development.

Before interpreting or using any contents, confirm the following:

1. Repository Status  
   - Read REPOSITORY_STATUS.md
   - Confirm the repository is marked as frozen

2. Version Separation  
   - Each major version has its own directory
   - Each release directory contains a README

3. Verification Evidence  
   - final_archive/ contains authoritative forensic outputs
   - security_manifests/ contains integrity hashes

4. Expected Behavior  
   - Lockouts, halts, and self-termination are valid outcomes
   - Stability does not imply availability

5. Modification Rules  
   - Frozen releases must not be modified
   - Any future work must occur in a separate fork

6. Reproducibility  
   - Scripts may be re-run
   - Generated artifacts must not replace archived evidence

If any of these conditions are not met, the repository should be treated as
invalid or incomplete.
