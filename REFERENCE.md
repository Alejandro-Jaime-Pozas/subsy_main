.github\workflows\checks.yml
- if .env files CHANGE will need to modify github secrets which are a base64 encoded via git bash CLI and include all contents of each file..
- checks.yml then decodes the encoded .env files for use in the env
