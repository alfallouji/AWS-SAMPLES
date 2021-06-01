/**
 * Face Detection Helper class
 */
var faceDetectionHelper = {

    /**
     * Flag indicating if tracking has started or not
     * @var boolean
     */
    trackingStarted: false,

    /**
     * Instance of clm tracker object
     * @var clm
     */
    ctrack: new clm.tracker(),

    /**
     * Flag indicating if 
     * @var boolean
     */
    flowStarted: false,

    /**
     * Number of similar/sequential captures 
     * @var int
     */
    similarCaptures: 0,

    /**
     * Threshold of captures needed before capturing a face
     * @var int
     */
    limitCaptures: 60,

    /**
     * Html Canvas object used to capture the image
     * @var Canvas
     */
    canvasOverlay: null,

    overlayCC: null,

    /**
     * Html Canvas object used to capture the image
     * @var Canvas
     */
    canvasImage: null,

    imageCC: null,

    /**
     * Data URI of captured Image
     * @var string
     */
    capturedImage: null,
   
    /**
     * AWS Lex Kathy object
     * @var Kathy
     */
    kathy: null,

    /**
     * Video Element
     * @var Video Html Video Element
     */
    video: null,

    /**
     * Init method
     * @var Video Html Video Element
     * @return void
     */
    init: function(video) { 
        this.video = video;
        navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
        window.URL = window.URL || window.webkitURL || window.msURL || window.mozURL;

        // set up video
        if (navigator.mediaDevices) {
            navigator.mediaDevices.getUserMedia({video : true}).then(this.gumSuccess).catch(this.gumFail);
        } else if (navigator.getUserMedia) {
            navigator.getUserMedia({video : true}, this.gumSuccess, this.gumFail);
        } else {
            alert("Your browser does not seem to support getUserMedia, using a fallback video instead.");
        }

        this.ctrack.init();
        this.trackingStarted = false;
    },

    /**
     * Start camera recording
     * @var Canvas canvasOverlay Canvas HTML Element
     * @var Canvas canvasImage Overlay HTML Element
     * @var Image capturedImage Image HTML Element
     * @return void
     */
    startVideo: function(canvasOverlay, canvasImage, capturedImage) { 
        // start video
        this.video.play();
        // start tracking
        this.ctrack.start(this.video);
        this.trackingStarted = true;
        this.canvasOverlay = canvasOverlay;
        this.overlayCC = canvasOverlay.getContext('2d');
        this.canvasImage = canvasImage;
        this.imageCC = canvasImage.getContext('2d');
        this.capturedImage = capturedImage;
    },

    /** 
     * Locate a face
     * @return string Image data
     */
    locateFace: function() {
        requestAnimFrame(faceDetectionHelper.locateFace);
        faceDetectionHelper.overlayCC.clearRect(0, 0, faceDetectionHelper.canvasOverlay.width, faceDetectionHelper.canvasOverlay.height);
        var positions = null;
        if (positions = faceDetectionHelper.ctrack.getCurrentPosition()) {
            // draw mask
            faceDetectionHelper.ctrack.draw(faceDetectionHelper.canvasOverlay);
            
            // Draw bounding box
            var left = positions[0][0] - 60;
            var right = positions[14][0] + 60;
            var top = (positions[33][1] - 0.9 * (positions[7][1] - positions[33][1]));
            var bottom = positions[7][1] + 60;
            faceDetectionHelper.drawBox(left, right, top, bottom, faceDetectionHelper.overlayCC);

            if (faceDetectionHelper.flowStarted == false) {
                if (faceDetectionHelper.similarCaptures == faceDetectionHelper.limitCaptures) {
                    console.log('got ' + faceDetectionHelper.limitCaptures + ' in a row - lets start the flow...');
                    faceDetectionHelper.extractImage(left, right, top, bottom);
                } else {
                    faceDetectionHelper.similarCaptures++;
                }
            } 
        }
        else {
            if (faceDetectionHelper.flowStarted == false && faceDetectionHelper.similarCaptures > 0) {
                // @todo : might want to adjust the penalty when not detecting a face 
                faceDetectionHelper.similarCaptures--;
            }
        }
    },

    /**
     * Extract image based on coordinates
     * @var int left Left position
     * @var int right right position
     * @var int top Top position
     * @var int bottom Bottom position
     * @return string Image (dataURI)
     */
    extractImage: function(left, right, top, bottom) {
        this.flowStarted = true;
        this.sendMessage('I found a face', false);
        this.canvasImage.width =  right - left;
        this.canvasImage.height = bottom - top;
        this.imageCC.drawImage(this.video, left-100, top-30, (right - left), (bottom - top), 0, 0, (right - left), (bottom - top));
        var dataURI = this.canvasImage.toDataURL('image/png', 1);
     
        // Render image 
        this.capturedImage.style.height = '150px';
        this.capturedImage.src = dataURI;
        this.capturedImage.style.border = "7px solid #333";

        return dataURI;
    },

    /**
     * Draw a bounding box around the detected face
     * @var int left Left position
     * @var int right Right position
     * @var int top Top position
     * @var int bottom Bottom position
     * @var int canvas Canvas to draw over
     * @return void
     */
    drawBox: function(left, right, top, bottom, canvas) {
        // draw bounding box
        canvas.strokeStyle = "#000";
        canvas.strokeRect(left, top, (right - left), (bottom - top));
        canvas.strokeStyle = "#82ff32";

        canvas.fillStyle = "#111";
        canvas.fillRect(0, 0, left, this.canvasOverlay.height);
        canvas.fillRect(right, 0, (this.canvasOverlay.width - right), this.canvasOverlay.height);
        canvas.fillRect(left - 1, 0, (right - left) + 2, top);
        canvas.fillRect(left, bottom, (right - left), (this.canvasOverlay.height - bottom));
    },

    /**
     * Send a message
     * @var string m Message to send
     * @var boolean speak Boolean flag indicating if message should be spoken (via Poly)
     * @return void
     */
    sendMessage: function(m, speak) {
        return new Promise(function(resolve, reject) {
            messageBox.innerHTML = m;
            if (speak) {
                this.kathy.SpeakWithPromise(m).then(function() {
                    if (this.kathy.IsSpeaking()) {
                        this.kathy.ShutUp();
                    }
                    this.kathy.ForgetCachedSpeech();
                    resolve();
                });
            }
        });
    },

    /**
     * Adjust video proportions
     * @return void
     */
    adjustVideoProportions: function() {
        // resize overlay and video if proportions of video are not 4:3
        // keep same height, just change width
        var proportion = this.video.videoWidth/this.video.videoHeight;
        vid_width = Math.round(this.video.height * proportion);
        this.video.width = vid_width;
        this.canvasOverlay.width = vid_width;
    },

    /**
     * Get User Media success check
     * @var stream stream Stream
     * @return void
     */
    gumSuccess: function(stream) {
        // add camera stream if getUserMedia succeeded
        if ("srcObject" in vid) {
            this.video.srcObject = stream;
        } else {
            this.video.src = (window.URL && window.URL.createObjectURL(stream));
        }
        this.video.onloadedmetadata = function() {
            faceDetectionHelper.adjustVideoProportions();
            faceDetectionHelper.video.play();
        }
        this.video.onresize = function() {
            faceDetectionHelper.adjustVideoProportions();
            if (faceDetectionHelper.trackingStarted) {
                faceDetectionHelper.ctrack.stop();
                faceDetectionHelper.ctrack.reset();
                faceDetectionHelper.ctrack.start(faceDetectionHelper.video);
            }
        }
    },

    /**
     * Get User Media fail
     * @return void
     */
    gumFail: function() {
        // @todo : fall back to video if getUserMedia failed
        //document.getElementById('gum').className = "hide";
        //document.getElementById('nogum').className = "nohide";
        console.log("There was some problem trying to fetch video from your webcam, using a fallback video instead.");
    },

    /**
     * Transform from base64 to ArrayBuffer
     * @var string base64 Base 64 encoded string
     * @return ArrayBuffer
     */
    base64ToArrayBuffer: function(base64) {
        var binary_string =  window.atob(base64);
        var len = binary_string.length;
        var bytes = new Uint8Array( len );
        for (var i = 0; i < len; i++)        {
            bytes[i] = binary_string.charCodeAt(i);
        }
        return bytes.buffer;
    }
};
