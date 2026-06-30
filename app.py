import os
import sys
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


from predict import predict

app = FastAPI(title="Anti-Spoofing Screen Detector")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/predict")
async def api_predict(file: UploadFile = File(...)):
    try:
       
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            

        score = predict(file_path)
        

        os.remove(file_path)
        

        classification = "Screen / Spoof Attempt" if score > 0.5 else "Real Physical Object"
        confidence = score if score > 0.5 else (1.0 - score)
        
        return {
            "success": True,
            "score": score,
            "classification": classification,
            "confidence": f"{confidence * 100:.2f}%"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Anti-Spoofing AI Demo</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-900 text-white font-sans min-h-screen flex flex-col items-center justify-center p-6">
        <div class="max-w-md w-full bg-slate-800 rounded-2xl shadow-xl border border-slate-700 p-6 text-center">
            <h1 class="text-2xl font-bold mb-2 text-indigo-400">🛡️ Anti-Spoofing Detector</h1>
            <p class="text-sm text-slate-400 mb-6">Choose an option below to evaluate if the image is an authentic scene or a screen recapture.</p>
            
            <div class="grid grid-cols-2 gap-4 mb-6">
                <label class="flex flex-col items-center justify-center p-5 bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/40 rounded-xl cursor-pointer transition group">
                    <svg class="w-8 h-8 text-indigo-400 group-hover:scale-105 transition mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                        <circle cx="12" cy="13" r="3"/>
                    </svg>
                    <span class="text-xs font-semibold tracking-wide">📸 Use Camera</span>
                    <input type="file" id="cameraInput" accept="image/*" capture="environment" class="hidden" onchange="processImage('cameraInput')"/>
                </label>

                <label class="flex flex-col items-center justify-center p-5 bg-slate-700/60 hover:bg-slate-700 border border-slate-600 rounded-xl cursor-pointer transition group">
                    <svg class="w-8 h-8 text-slate-400 group-hover:scale-105 transition mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
                    </svg>
                    <span class="text-xs font-semibold tracking-wide">📁 Upload Image</span>
                    <input type="file" id="fileInput" accept="image/*" class="hidden" onchange="processImage('fileInput')"/>
                </label>
            </div>
            
            <div id="loader" class="hidden text-sm text-indigo-300 animate-pulse mb-4 font-medium">Analyzing spatial configurations...</div>
            
            <div id="resultBox" class="hidden p-4 rounded-xl border text-left bg-slate-850">
                <h3 class="text-xs uppercase font-bold text-slate-400 tracking-wider mb-1">Analysis Verdict</h3>
                <div id="verdict" class="text-lg font-bold mb-2"></div>
                <div class="text-sm text-slate-300">Confidence Metric: <span id="confidence" class="font-semibold text-white"></span></div>
                <div class="text-xs text-slate-500 mt-2">Raw Classification Boundary: <span id="rawScore"></span></div>
            </div>
        </div>

        <script>
            async function processImage(inputId) {
                const input = document.getElementById(inputId);
                if (!input.files || input.files.length === 0) return;
                
                const file = input.files[0];
                const formData = new FormData();
                formData.append('file', file);
                
                // Reset states
                document.getElementById('loader').classList.remove('hidden');
                document.getElementById('resultBox').classList.add('hidden');
                
                try {
                    const response = await fetch('/api/predict', { method: 'POST', body: formData });
                    const data = await response.json();
                    
                    document.getElementById('loader').classList.add('hidden');
                    if (!data.success) { alert("Error analyzing file image."); return; }
                    
                    const box = document.getElementById('resultBox');
                    const verdict = document.getElementById('verdict');
                    
                    box.classList.remove('hidden');
                    verdict.innerText = data.classification;
                    document.getElementById('confidence').innerText = data.confidence;
                    document.getElementById('rawScore').innerText = data.score;
                    
                    if (data.score > 0.5) {
                        box.className = "p-4 rounded-xl border border-red-500/60 bg-red-950/20 text-red-200 mt-4";
                        verdict.className = "text-lg font-bold text-red-400";
                    } else {
                        box.className = "p-4 rounded-xl border border-emerald-500/60 bg-emerald-950/20 text-emerald-200 mt-4";
                        verdict.className = "text-lg font-bold text-emerald-400";
                    }
                } catch (err) {
                    document.getElementById('loader').classList.add('hidden');
                    alert("Network error connecting to runtime service.");
                }
                
                // Clear inputs so the same file can be captured consecutively
                input.value = "";
            }
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)


