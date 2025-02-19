.github\workflows\checks.yml
- if .env files CHANGE will need to modify github secrets which are a base64 encoded via git bash CLI and include all contents of each file..
- code for the above, open wsl cli
  - base64 input_file_path
  - copy and paste to editor to remove newlines
  - copy and paste into github env secret to update
- checks.yml then decodes the encoded .env files for use in the env
