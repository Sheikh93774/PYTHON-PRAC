const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let streamlit;

function createWindow () {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      contextIsolation: false,
      nodeIntegration: true,
    },
    icon: path.join(__dirname, 'app/assets/coastal_bg.jpg') // optional icon
  });

  streamlit = spawn('streamlit', ['run', 'app/main.py']);

  streamlit.stdout.on('data', (data) => {
    const line = data.toString();
    const match = line.match(/http:\/\/localhost:\\d+/);
    if (match && mainWindow) {
      mainWindow.loadURL(match[0]);
    }
  });

  streamlit.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  streamlit.on('close', (code) => {
    console.log(`Streamlit closed with code ${code}`);
    app.quit();
  });
}

app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    if (streamlit) streamlit.kill();
    app.quit();
  }
});
