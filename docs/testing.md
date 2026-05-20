# Testing

Run the layout verifier from the repository root:

```bash
scripts/validate-plugin-layout.sh
```

Run fixture validators:

```bash
python3 skills/create-prd/scripts/validate_prd.py tests/fixtures/add-relu/prd.md --operator AddRelu
python3 skills/create-spec/scripts/validate_spec.py tests/fixtures/add-relu/spec.md --operator AddRelu
```

Review YAML validators are exercised by Mozi review workflows after they write draft YAML to a temporary file.
