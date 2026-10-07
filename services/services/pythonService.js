const { spawn } = require('child_process');
const path = require('path');

/**
 * Node.js Python Prediction Service
 * Invokes python bridge script asynchronously with JSON payloads.
 */
function runPythonPrediction(inputData) {
  return new Promise((resolve, reject) => {
    const pythonScript = path.join(__dirname, '..', 'predict_bridge.py');
    const pyProcess = spawn('python', [pythonScript]);

    let stdoutData = '';
    let stderrData = '';

    pyProcess.stdout.on('data', (data) => {
      stdoutData += data.toString();
    });

    pyProcess.stderr.on('data', (data) => {
      stderrData += data.toString();
    });

    pyProcess.on('close', (code) => {
      if (code !== 0) {
        return reject(new Error(`Python bridge process exited with code ${code}: ${stderrData}`));
      }
      try {
        const result = JSON.parse(stdoutData);
        resolve(result);
      } catch (err) {
        reject(new Error(`Failed to parse Python output: ${err.message}`));
      }
    });

    pyProcess.stdin.write(JSON.stringify(inputData));
    pyProcess.stdin.end();
  });
}

module.exports = {
  runPythonPrediction,
};
