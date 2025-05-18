"# Eye tracker module" 
FocusLoop Webcam Eye Tracker Module
This module replaces the Tobii 5L hardware eye tracker with a webcam-based solution using GazeCloudAPI. It maintains all the functionality described in the original Eye-Tracker Dispersion Module, including BCEA (Bivariate Contour Ellipse Area) calculation and dispersion scoring.
Features

Uses standard webcam for eye tracking via GazeCloudAPI
Calculates real-time dispersion score at 10Hz (configurable)
Computes Bivariate Contour Ellipse Area (BCEA) from gaze data
Normalizes dispersion scores based on per-user calibration
Publishes data via ZeroMQ compatible with existing FocusLoop architecture
Provides fallback WebSocket communication for the OSC bridge
Includes visual monitoring dashboard

Installation

Register your domain with GazeCloudAPI at https://api.gazerecorder.com/register/
Add the following files to your FocusLoop project structure:

webcam_eye_tracker.js - Core implementation
webcam_eye_tracker_demo.html - Dashboard/demo page


Make sure you include the required dependencies:

html<script src="https://api.gazerecorder.com/GazeCloudAPI.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/zeromq.js/6.0.0-beta.9/zeromq.min.js"></script>
Integration with FocusLoop
This module is designed as a drop-in replacement for the Tobii 5L implementation. It publishes dispersion scores in the same format and frequency expected by other FocusLoop components.
Data Flow

Webcam captures eye movements via GazeCloudAPI
Raw gaze data is processed in a 500ms rolling window
BCEA is calculated and normalized to a 0-1 dispersion score
Scores are published via ZeroMQ on /dispersion_score topic
OSC Bridge receives and forwards to Unity as before

Configuration
Key parameters can be adjusted in the CONFIG object at the top of webcam_eye_tracker.js:

windowSize: Rolling window size in milliseconds (default: 500)
publishRate: How often to publish dispersion scores in Hz (default: 10)
minValidSamples: Minimum fraction of valid samples required (default: 0.6)
zmqPublishTopic: ZeroMQ topic for publishing (default: '/dispersion_score')
calibrationTime: Duration of baseline calibration in seconds (default: 30)
updateInterval: How often to process gaze data in milliseconds (default: 25)

API Reference
The module exposes a global WebcamEyeTracker object with the following methods:

init(): Initialize and start the eye tracker
startCalibration(): Begin baseline BCEA calibration
shutdown(): Stop tracking and clean up resources

Monitoring
A visual monitoring dashboard is available by opening webcam_eye_tracker_demo.html in a browser. This provides:

Real-time visualization of gaze points and BCEA ellipse
Current dispersion score and BCEA values
System status indicators
Controls for starting/stopping tracking and calibration

Differences from Tobii Implementation

Uses webcam instead of specialized hardware
Initial calibration is performed by GazeCloudAPI
Data sampling rate may be lower (typically ~30Hz vs Tobii's 120Hz)
BCEA calculation is performed in screen coordinates rather than degrees
May have higher latency (~100-150ms)

Technical Notes

The BCEA calculation uses a 95% confidence ellipse (2.291 sigma)
Dispersion is normalized using a sigmoid function for better scaling
GazeCloudAPI provides state flags similar to Tobii's valid flags
Insufficient valid samples result in null dispersion values
