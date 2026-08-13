const fs = require('fs');

for (const name of [
  'ACTIONS_CACHE_URL',
  'ACTIONS_RUNTIME_TOKEN',
  'ACTIONS_RESULTS_URL',
  'ACTIONS_CACHE_SERVICE_V2',
]) {
  const value = process.env[name];
  if (!value) continue;
  fs.appendFileSync(process.env.GITHUB_ENV, `${name}<<GHA_CACHE_ENV\n${value}\nGHA_CACHE_ENV\n`);
}
