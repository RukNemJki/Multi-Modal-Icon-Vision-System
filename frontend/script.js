// Multi-Modal Icon Vision System - Frontend JavaScript

const API_BASE_URL = 'http://localhost:5000';

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const detectButton = document.getElementById('detectButton');
const resultsSection = document.getElementById('resultsSection');
const resultCanvas = document.getElementById('resultCanvas');
const loadingSpinner = document.getElementById('loadingSpinner');
const confidenceSlider = document.getElementById('confidenceSlider');
const confidenceValue = document.getElementById('confidenceValue');
const iouSlider = document.getElementById('iouSlider');
const iouValue = document.getElementById('iouValue');
const downloadButton = document.getElementById('downloadButton');

// State
let selectedFile = null;
let currentResults = null;
let startTime = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    checkAPIStatus();
});

// Setup Event Listeners
function setupEventListeners() {
    // File input
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // Detect button
    detectButton.addEventListener('click', handleDetect);
    
    // Sliders
    confidenceSlider.addEventListener('input', (e) => {
        confidenceValue.textContent = e.target.value;
    });
    
    iouSlider.addEventListener('input', (e) => {
        iouValue.textContent = e.target.value;
    });
    
    // Download button
    downloadButton.addEventListener('click', handleDownload);
}

// Check API Status
async function checkAPIStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/`);
        const data = await response.json();
        console.log('API Status:', data);
    } catch (error) {
        console.error('API not available:', error);
        showNotification('Warning: Backend API not available. Please start the server.', 'warning');
    }
}

// File Selection Handlers
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        validateAndSetFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const file = event.dataTransfer.files[0];
    if (file) {
        validateAndSetFile(file);
    }
}

function validateAndSetFile(file) {
    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('Invalid file type. Please upload PNG or JPEG image.', 'error');
        return;
    }
    
    // Validate file size (10MB max)
    const maxSize = 10 * 1024 * 1024;
    if (file.size > maxSize) {
        showNotification('File too large. Maximum size is 10MB.', 'error');
        return;
    }
    
    selectedFile = file;
    displaySelectedFile(file);
    detectButton.disabled = false;
}

function displaySelectedFile(file) {
    // Update upload area to show selected file
    const reader = new FileReader();
    reader.onload = (e) => {
        uploadArea.innerHTML = `
            <div class="upload-icon">✓</div>
            <p class="upload-text">File selected: ${file.name}</p>
            <p class="upload-subtext">${formatFileSize(file.size)}</p>
            <label for="fileInput" class="upload-button">Choose Different File</label>
        `;
    };
    reader.readAsDataURL(file);
}

// Detection Handler
async function handleDetect() {
    if (!selectedFile) {
        showNotification('Please select an image first.', 'error');
        return;
    }
    
    // Show loading state
    loadingSpinner.style.display = 'block';
    resultCanvas.style.display = 'none';
    resultsSection.style.display = 'block';
    detectButton.disabled = true;
    detectButton.textContent = 'Detecting...';
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
    
    // Record start time
    startTime = Date.now();
    
    // Prepare form data
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('confidence', confidenceSlider.value);
    formData.append('iou', iouSlider.value);
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Detection failed');
        }
        
        const results = await response.json();
        currentResults = results;
        
        // Calculate processing time
        const processingTime = Date.now() - startTime;
        results.processingTime = processingTime;
        
        // Display results
        displayResults(results);
        
        showNotification('Detection completed successfully!', 'success');
        
    } catch (error) {
        console.error('Detection error:', error);
        showNotification('Detection failed. Please try again.', 'error');
        loadingSpinner.style.display = 'none';
    } finally {
        detectButton.disabled = false;
        detectButton.textContent = 'Detect Icons';
    }
}

// Display Results
function displayResults(results) {
    loadingSpinner.style.display = 'none';
    
    // Load and display image
    const reader = new FileReader();
    reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
            drawDetections(img, results.detections);
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(selectedFile);
    
    // Update statistics
    updateStatistics(results);
    
    // Display detections list
    displayDetectionsList(results.detections);
}

function drawDetections(img, detections) {
    const canvas = resultCanvas;
    const ctx = canvas.getContext('2d');
    
    // Set canvas size to match image
    canvas.width = img.width;
    canvas.height = img.height;
    
    // Draw image
    ctx.drawImage(img, 0, 0);
    
    // Draw detections
    detections.forEach((det, index) => {
        const bbox = det.bbox;
        const color = getColorForClass(det.class_id);
        
        // Draw rectangle
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.strokeRect(bbox.x1, bbox.y1, bbox.width, bbox.height);
        
        // Draw label background
        const label = `${det.class_name}: ${(det.confidence * 100).toFixed(1)}%`;
        ctx.font = 'bold 16px Arial';
        const textMetrics = ctx.measureText(label);
        const textHeight = 20;
        
        ctx.fillStyle = color;
        ctx.fillRect(bbox.x1, bbox.y1 - textHeight - 5, textMetrics.width + 10, textHeight + 5);
        
        // Draw label text
        ctx.fillStyle = 'white';
        ctx.fillText(label, bbox.x1 + 5, bbox.y1 - 8);
    });
    
    canvas.style.display = 'block';
}

function updateStatistics(results) {
    // Total detections
    document.getElementById('totalDetections').textContent = results.num_detections;
    
    // Average confidence
    if (results.num_detections > 0) {
        const avgConf = results.detections.reduce((sum, det) => sum + det.confidence, 0) / results.num_detections;
        document.getElementById('avgConfidence').textContent = `${(avgConf * 100).toFixed(1)}%`;
    } else {
        document.getElementById('avgConfidence').textContent = 'N/A';
    }
    
    // Processing time
    document.getElementById('processingTime').textContent = `${results.processingTime}ms`;
}

function displayDetectionsList(detections) {
    const listContainer = document.getElementById('detectionsList');
    
    if (detections.length === 0) {
        listContainer.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">No icons detected</p>';
        return;
    }
    
    listContainer.innerHTML = detections.map((det, index) => `
        <div class="detection-item">
            <div class="class-name">${det.class_name.replace(/_/g, ' ')}</div>
            <div class="confidence">Confidence: ${(det.confidence * 100).toFixed(1)}%</div>
            <div class="bbox-info">
                Position: (${Math.round(det.bbox.x1)}, ${Math.round(det.bbox.y1)})<br>
                Size: ${Math.round(det.bbox.width)}×${Math.round(det.bbox.height)}px
            </div>
        </div>
    `).join('');
}

// Download Handler
function handleDownload() {
    if (!currentResults) {
        showNotification('No results to download', 'error');
        return;
    }
    
    // Download annotated image
    const link = document.createElement('a');
    link.download = `icon_detection_${Date.now()}.png`;
    link.href = resultCanvas.toDataURL();
    link.click();
    
    // Also download JSON results
    downloadJSON(currentResults, `detection_results_${Date.now()}.json`);
    
    showNotification('Results downloaded successfully!', 'success');
}

function downloadJSON(data, filename) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.download = filename;
    link.href = URL.createObjectURL(blob);
    link.click();
}

// Utility Functions
function getColorForClass(classId) {
    const colors = [
        '#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16',
        '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
        '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef',
        '#ec4899', '#f43f5e', '#fb7185', '#fb923c', '#fbbf24',
        '#a3e635', '#4ade80', '#34d399', '#2dd4bf', '#22d3ee',
        '#38bdf8'
    ];
    return colors[classId % colors.length];
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
