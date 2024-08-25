const express = require('express');
const multer = require('multer');
const AWS = require('aws-sdk');

const app = express();
const port = 3000;

app.use(express.static('public')); // Serve static files from 'public' directory

// Configure AWS SDK
AWS.config.update({
  region: 'us-west-2', // Update with your region
  accessKeyId: 'YOUR_ACCESS_KEY_ID',
  secretAccessKey: 'YOUR_SECRET_ACCESS_KEY'
});

const s3 = new AWS.S3();
const ses = new AWS.SES();

const upload = multer({ storage: multer.memoryStorage() });

app.post('/launch_ec2', (req, res) => {
  // Handle EC2 instance launch logic here
  res.send('EC2 instance launch request received.');
});

app.post('/deploy_rhel_gui', (req, res) => {
  // Handle RHEL GUI instance deployment logic here
  res.send('RHEL GUI instance deployment request received.');
});

app.post('/access_logs', (req, res) => {
  // Handle CloudWatch logs retrieval logic here
  res.send('Access logs request received.');
});

app.post('/event_driven', (req, res) => {
  // Handle event-driven architecture with S3 and Transcribe logic here
  res.send('Event-driven architecture setup request received.');
});

app.post('/python_lambda', (req, res) => {
  // Handle Python to MongoDB via Lambda connection logic here
  res.send('Python to MongoDB Lambda connection request received.');
});

app.post('/upload_s3', upload.single('file'), (req, res) => {
  const params = {
    Bucket: req.body.bucketName,
    Key: req.file.originalname,
    Body: req.file.buffer
  };

  s3.upload(params, (err, data) => {
    if (err) {
      res.status(500).send('Error uploading file.');
    } else {
      res.send('File uploaded successfully.');
    }
  });
});

app.post('/lambda_s3', upload.single('emailFile'), (req, res) => {
  const params = {
    Bucket: req.body.bucketName,
    Key: req.file.originalname,
    Body: req.file.buffer
  };

  s3.upload(params, (err, data) => {
    if (err) {
      res.status(500).send('Error uploading file.');
    } else {
      // Process the file with Lambda
      // Here you would typically invoke a Lambda function
      res.send('File uploaded and Lambda function triggered.');
    }
  });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}/`);
});
