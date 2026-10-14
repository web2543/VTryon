const baseInput = document.getElementById("base-image");
const clothInput = document.getElementById("cloth-image");

const basePreview = document.getElementById("base-preview");
const clothPreview = document.getElementById("cloth-preview");

const generateBtn = document.getElementById("generate-btn");
const statusEl = document.getElementById("status");
const outputBox = document.getElementById("output-box");
const spinner = document.getElementById("spinner");
const resultImage = document.getElementById("result-image");
const outputPlaceholder = document.getElementById("output-placeholder");

let payloads = { base: null, cloth: null };

function setPreview(inputEl, previewEl, dataUrl) {
    if (!dataUrl) {
        previewEl.textContent = "No image selected";
        previewEl.innerHTML = "";
        return;
    }
    const img = document.createElement("img");
    img.src = dataUrl;
    previewEl.textContent = "";
    previewEl.appendChild(img);
}

function readFileAsDataURL(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function downscaleDataURL(dataUrl, maxSize = 2048) {
    return new Promise((resolve) => {
        const img = new Image();
        img.onload = () => {
            let w = img.naturalWidth;
            let h = img.naturalHeight;
            if (w <= maxSize && h <= maxSize) {
                resolve(dataUrl);
                return;
            }
            if (w > h) {
                h = Math.round((h * maxSize) / w);
                w = maxSize;
            } else {
                w = Math.round((w * maxSize) / h);
                h = maxSize;
            }
            const canvas = document.createElement("canvas");
            canvas.width = w;
            canvas.height = h;
            const ctx = canvas.getContext("2d");
            ctx.drawImage(img, 0, 0, w, h);
            resolve(canvas.toDataURL("image/png"));
        };
        img.onerror = () => resolve(dataUrl);
        img.src = dataUrl;
    });
}

function handleFileSelect(key) {
    return async (e) => {
        const file = e.target.files[0];
        if (!file) {
            payloads[key] = null;
            const previewMap = { base: basePreview, cloth: clothPreview };
            setPreview(e.target, previewMap[key], null);
            updateButton();
            return;
        }
        try {
            const dataUrl = await readFileAsDataURL(file);
            const scaled = await downscaleDataURL(dataUrl);
            payloads[key] = scaled;
            const previewMap = { base: basePreview, cloth: clothPreview };
            setPreview(e.target, previewMap[key], scaled);
        } catch {
            setStatus("Failed to read image", "error");
        }
        updateButton();
    };
}

baseInput.addEventListener("change", handleFileSelect("base"));
clothInput.addEventListener("change", handleFileSelect("cloth"));

function updateButton() {
    generateBtn.disabled = !(payloads.base && payloads.cloth);
}

function setStatus(text, type = "") {
    statusEl.textContent = text;
    statusEl.className = type;
}

function showSpinner() {
    spinner.classList.remove("hidden");
    resultImage.classList.add("hidden");
    outputPlaceholder.classList.add("hidden");
}

function showResult(dataUrl) {
    spinner.classList.add("hidden");
    resultImage.src = dataUrl;
    resultImage.classList.remove("hidden");
    outputPlaceholder.classList.add("hidden");
}

function showPlaceholder() {
    spinner.classList.add("hidden");
    resultImage.classList.add("hidden");
    outputPlaceholder.classList.remove("hidden");
}

generateBtn.addEventListener("click", async () => {
    generateBtn.disabled = true;
    setStatus("Generating...", "loading");
    showSpinner();

    try {
        const response = await fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                base_image: payloads.base,
                cloth_image: payloads.cloth,
            }),
            signal: AbortSignal.timeout(60000),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || `Server error ${response.status}`);
        }

        showResult(data.gen_image);
        setStatus("Done!");
    } catch (err) {
        if (err.name === "AbortError") {
            setStatus("Request timed out (60s). Please try again.", "error");
        } else {
            setStatus(err.message || "Generation failed", "error");
        }
        showPlaceholder();
    } finally {
        updateButton();
    }
});
