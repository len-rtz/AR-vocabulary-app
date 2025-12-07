import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:logger/logger.dart';
import 'dart:async';
import 'package:http_parser/http_parser.dart'; 

// --- CONFIGURATION ---
const bool USE_MOCK_DATA = false; // Set to FALSE for real backend

// Ensure your computer and phone are on the same network.
// Replace with your actual local IP address.
const String BASE_BACKEND_URL = 'http://172.20.10.3:8000';
const String TRANSLATE_ENDPOINT = '$BASE_BACKEND_URL/translate';
const String RECALL_ENDPOINT = '$BASE_BACKEND_URL/recall';

// Initialize logger instance
final logger = Logger(
  printer: PrettyPrinter(
    methodCount: 0,
    printTime: true,
  ),
);

// --- MOCK BACKEND DATA ---
final Map<String, dynamic> MOCK_TRANSLATION_RESPONSES = {
  'CUP_ID_1': {
    'target_word': 'cupă',
    'modality': 'AR_TEXT_AUDIO',
    'object_name': 'cup',
  },
  'SPOON_ID_2': {
    'target_word': 'lingură',
    'modality': 'TRADITIONAL_TEXT_AUDIO',
    'object_name': 'spoon',
  },
};

class ScannerScreen extends StatefulWidget {
  const ScannerScreen({super.key});

  @override
  State<ScannerScreen> createState() => _ScannerScreenState();
}

class _ScannerScreenState extends State<ScannerScreen> {
  // --- STATE VARIABLES AND CONTROLLERS ---
  // Using default controller settings which work for most devices
  final MobileScannerController scannerController = MobileScannerController();
  final FlutterTts flutterTts = FlutterTts();
  final recorder = AudioRecorder();
  final int _participantId = 1; // or your real participant ID

  // Variables updated via setState()
  String _currentWord = '';
  String _currentModality = '';
  // Added to store marker ID for recall submission
  String _currentMarkerId = ''; 
  bool _isRecording = false;
  final List<Map<String, dynamic>> _sessionStats = [];

  // --- LIFECYCLE METHODS ---
  @override
  void initState() {
    super.initState();
    _initTts();
  }

  @override
  void dispose() {
    scannerController.dispose();
    flutterTts.stop();
    recorder.dispose();
    super.dispose();
  }

  // --- TTS and Speech Functions ---
  Future _initTts() async {
    await flutterTts.setLanguage("ro-RO");
    await flutterTts.setSpeechRate(0.5);
  }

  Future _speak(String text) async {
    await flutterTts.speak(text);
  }

  void _presentTranslation(String word, String modality, String markerId) {
    setState(() {
      _currentWord = word;
      _currentModality = modality;
      _currentMarkerId = markerId; // Store marker ID
    });

    logger.d('State set. New word: $_currentWord, Modality: $modality, ID: $markerId');

    if (modality.contains('AUDIO')) {
      _speak(word);
    }
  }

  // --- TRANSLATION HANDLER (MOCK OR LIVE) ---
  void _handleScan(String markerId) async {
    logger.d('RAW DETECTED VALUE: $markerId');

    String targetWord = '';
    String modality = '';

    if (USE_MOCK_DATA) {
      // --- MOCK LOGIC ---
      await Future.delayed(const Duration(milliseconds: 500));

      if (MOCK_TRANSLATION_RESPONSES.containsKey(markerId)) {
        final data = MOCK_TRANSLATION_RESPONSES[markerId]!;
        targetWord = data['target_word'];
        modality = data['modality'];
        logger.i('MOCK: Translation successful for ID: $markerId');
      } else {
        logger.w('MOCK ERROR: Marker ID "$markerId" not recognized. Resuming scan.');
        scannerController.start();
        return;
      }
    } else {
      // --- REAL NETWORK LOGIC ---
      logger.i('LIVE: Sending translation request to $TRANSLATE_ENDPOINT');
      try {
        final response = await http.post(
          Uri.parse(TRANSLATE_ENDPOINT),
          headers: {'Content-Type': 'application/json; charset=UTF-8'},
          body: jsonEncode({'marker_id': markerId,
          'participant_id': _participantId}), // or your real participant ID
        );

        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          targetWord = data['target_word'];
          modality = data['modality'];
          logger.i('LIVE: Translation received successfully.');
        } else {
          logger.e('API Error ${response.statusCode}: Failed to fetch translation.');
          scannerController.start();
          return;
        }
      } catch (e) {
        logger.e('Network Error: Could not connect to backend.', error: e);
        scannerController.start();
        return;
      }
    }

    // Final presentation if data was successfully obtained
    _presentTranslation(targetWord, modality, markerId);
  }

  // --- RECORDING HANDLER ---
 /* void _recordAndSubmit() async {
    if (_currentWord.isEmpty || _isRecording) return;

    final hasPermission = await recorder.hasPermission();
    if (!hasPermission) {
      logger.e('Microphone permission denied.');
      return;
    }

    try {
      setState(() => _isRecording = true);

      final tempDir = await getTemporaryDirectory();
      final filePath =
          '${tempDir.path}/temp_recall_${DateTime.now().millisecondsSinceEpoch}.m4a';

      await recorder.start(
        const RecordConfig(
          encoder: AudioEncoder.aacLc,
          bitRate: 128000,
          sampleRate: 44100,
        ),
        path: filePath,
      );

      logger.i('Recording started...');

      // Record for 3 seconds
      await Future.delayed(const Duration(seconds: 3));

      final recordedPath = await recorder.stop();
      setState(() => _isRecording = false);

      if (recordedPath == null) {
        logger.w('Recording failed or file path is null');
        return;
      }

      logger.i('Recording stopped. File saved at: $recordedPath');
      
      // Submit the recording
      _submitRecall(recordedPath, _currentWord, _currentMarkerId);

    } catch (e) {
      logger.e('Error during recording process', error: e);
      setState(() => _isRecording = false);
    }
  }
*/
  void _recordAndSubmit() async {
    logger.d("Attempting to record...");

    if (_currentWord.isEmpty) {
    logger.w("Recording aborted: _currentWord is empty.");
    return;
  }
  if (_isRecording) {
    logger.w("Recording aborted: Already recording.");
    return;
  }

   

  final hasPermission = await recorder.hasPermission();
  if (!hasPermission) {
    logger.e('Microphone permission denied.');
    return;
  }

  try {
    setState(() => _isRecording = true);

    final tempDir = await getTemporaryDirectory();
    final filePath =
        '${tempDir.path}/temp_recall_${DateTime.now().millisecondsSinceEpoch}.m4a';

    // 1️⃣ Start recording
    await recorder.start(
      const RecordConfig(
        encoder: AudioEncoder.aacLc,
        bitRate: 128000,
        sampleRate: 44100,
      ),
      path: filePath,
    );

    logger.i('Recording started...');

    // Record for 3 seconds
    await Future.delayed(const Duration(seconds: 3));

    // 2️⃣ Stop recording
    final recordedPath = await recorder.stop();
    setState(() => _isRecording = false);

    if (recordedPath == null) {
      logger.w('Recording failed or file path is null');
      return;
    }

    logger.i('Recording stopped. File saved at: $recordedPath');

    // 3️⃣ SEND TO BACKEND
    final uri = Uri.parse("$BASE_BACKEND_URL/recall");

    var request = http.MultipartRequest("POST", uri)
      ..fields["target_word"] = _currentWord
      ..fields["marker_id"] = _currentMarkerId
      ..fields["participant_id"] = "0"           // or your real participant ID
      ..fields["session_id"] = "0"               // or your real session ID
      ..files.add(
        await http.MultipartFile.fromPath(
          "audio_file",        // must match FastAPI parameter name
          recordedPath,
          contentType: MediaType("audio", "m4a"),
        ),
      );

    logger.i("Uploading recall audio...");

    var streamedResponse = await request.send();
    var response = await http.Response.fromStream(streamedResponse);

    logger.i("Recall response: ${response.statusCode}");
    logger.i("Response: ${response.body}");

    if (response.statusCode != 200) {
      logger.e("Recall submission failed.");
      return;
    }

    // 4️⃣ Show feedback + restart scanner
    _showFeedback(0.9, _currentWord);

  } catch (e) {
    logger.e('Error during recording process', error: e);
    setState(() => _isRecording = false);
  }
}

  
  // --- RECALL SUBMISSION HANDLER (MOCK OR LIVE) ---
 /* void _submitRecall(String audioFilePath, String targetWord, String markerId) async {
    double finalAccuracy = 0.0;
    String finalTranscription = '';

    if (USE_MOCK_DATA) {
      // --- MOCK LOGIC ---
      await Future.delayed(const Duration(seconds: 1));
      finalAccuracy = 0.95;
      finalTranscription = targetWord;
      logger.i('MOCK: Recall scored. Accuracy: $finalAccuracy');
    } else {
      // --- REAL NETWORK LOGIC ---
      logger.i('LIVE: Submitting audio file for scoring...');
      try {
        var request = http.MultipartRequest('POST', Uri.parse(RECALL_ENDPOINT));
        
        // Add required fields
        request.fields['target_word'] = targetWord;
        request.fields['marker_id'] = markerId; // Fixed: Now sending marker_id

        // Add file
        request.files.add(await http.MultipartFile.fromPath(
          'audio_file',
          audioFilePath,
          contentType: MediaType('audio', 'm4a'),
        ));

        var streamedResponse = await request.send();
        final response = await http.Response.fromStream(streamedResponse);

        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          // Handle backend response format
          // Backend currently returns {recall_id, message, audio_filename}
          // It DOES NOT return accuracy yet. We default to 1.0 for now.

          // finalAccuracy = (data['accuracy'] ?? 1.0).toDouble();
          // finalTranscription = data['transcription'] ?? targetWord;

          finalAccuracy = 0.9; // assume correct
          finalTranscription = targetWord;

          
          logger.i('LIVE: Recall submission successful. ID: ${data['recall_id']}');
        } else {
          logger.e('API Error ${response.statusCode}: ${response.body}');
          return;
        }
      } catch (e) {
        logger.e('Network Error: Could not submit audio to backend.', error: e);
        return;
      }
    }

    // Final feedback presentation
    _showFeedback(finalAccuracy, finalTranscription);
  }
*/
  // --- UI Feedback and State Management ---
  // void _showFeedback(double accuracy, String transcription) {
  //   String feedbackMessage = accuracy > 0.8
  //       ? 'Correct! Accuracy: ${(accuracy * 100).toStringAsFixed(0)}%'
  //       : 'Try again. Heard: "$transcription"';

  //   if (!mounted) return;

  //   ScaffoldMessenger.of(context).showSnackBar(
  //     SnackBar(content: Text(feedbackMessage)),
  //   );

  //   setState(() {
  //     _sessionStats.insert(0, {'word': _currentWord, 'accuracy': accuracy});
  //     if (_sessionStats.length > 5) _sessionStats.removeLast();

  //     // Reset state for next scan
  //     _currentWord = '';
  //     _currentMarkerId = '';
  //     // Resume scanner
  //     scannerController.start();
  //   });
  // }
  void _showFeedback(double accuracy, String transcription) {
  String feedbackMessage = accuracy > 0.8
      ? 'Correct! Accuracy: ${(accuracy * 100).toStringAsFixed(0)}%'
      : 'Try again. Heard: "$transcription"';

  if (!mounted) return;

  // Delay state reset slightly to allow SnackBar to appear
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(content: Text(feedbackMessage), duration: const Duration(seconds: 2)),
  );

  Future.delayed(const Duration(milliseconds: 500), () {
    if (!mounted) return;
    setState(() {
      _sessionStats.insert(0, {'word': _currentWord, 'accuracy': accuracy});
      if (_sessionStats.length > 5) _sessionStats.removeLast();
      _currentWord = '';
      _currentMarkerId = '';
      scannerController.start(); // restart camera after reset
    });
  });
}


  // --- BUILD METHODS ---
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Point, Scan, Learn')),
      body: _buildScannerView(),
    );
  }

  Widget _buildScannerView() {
  bool isAR = _currentModality == 'AR_TEXT_AUDIO';
  bool isTraditional = _currentModality == 'TRADITIONAL_TEXT_AUDIO';

  bool showText = isAR || isTraditional;
  bool showTraditionalImage = isTraditional;

  return Stack(
    children: [
      // Camera feed
      MobileScanner(
        controller: scannerController,
        onDetect: (capture) {
          if (capture.barcodes.isNotEmpty) {
            final barcode = capture.barcodes.first;
            final markerId = barcode.rawValue;

            if (markerId != null && _currentWord.isEmpty) {
              scannerController.stop();
              _handleScan(markerId);
            }
          }
        },
      ),

      // Reticle
      Center(
        child: Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            border: Border.all(color: Colors.red, width: 2),
            shape: BoxShape.circle,
          ),
        ),
      ),

      // TOP DISPLAY BOX — only show if there is a word
      if (_currentWord.isNotEmpty)
        Align(
          alignment: Alignment.topCenter,
          child: Padding(
            padding: const EdgeInsets.only(top: 80.0),
            child: Container(
              padding: const EdgeInsets.all(16.0),
              color: Colors.white70,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  if (showTraditionalImage)
                    Image.asset(
                      'assets/images/placeholder.png',
                      height: 100,
                    ),

                  if (showText)
                    Text(
                      _currentWord,
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),

      // RECORD BUTTON
      Align(
        alignment: Alignment.bottomCenter,
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: FloatingActionButton(
            onPressed:
                (_currentWord.isNotEmpty && !_isRecording) ? _recordAndSubmit : null,
            backgroundColor: _isRecording ? Colors.green : Colors.red,
            child: Icon(_isRecording ? Icons.mic : Icons.mic_off),
          ),
        ),
      ),

      // STATS
      if (_sessionStats.isNotEmpty)
        Positioned(
          bottom: 100,
          left: 20,
          child: Container(
            padding: const EdgeInsets.all(8),
            color: Colors.black54,
            child: Text(
              'Last Recall: ${_sessionStats.first['word']} (${(_sessionStats.first['accuracy'] * 100).toStringAsFixed(0)}%)',
              style: const TextStyle(color: Colors.white, fontSize: 14),
            ),
          ),
        ),
    ],
  );
}

}