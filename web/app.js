let model;
let metadata;
let maxLen;
let wordIndex;
let labels;

const recommendBtn = document.getElementById('recommendBtn');
const ingredientsInput = document.getElementById('ingredientsInput');
const resultSection = document.getElementById('resultSection');
const recipeTitle = document.getElementById('recipeTitle');
const confidenceFill = document.getElementById('confidenceFill');
const loader = document.getElementById('loader');
const btnText = recommendBtn.querySelector('.btn-text');

async function init() {
    try {
        console.log("Loading metadata...");
        const metaResponse = await fetch('metadata.json');
        metadata = await metaResponse.json();

        wordIndex = metadata.word_index;
        labels = metadata.labels;
        maxLen = metadata.max_len;

        console.log("Loading TFLite model...");
        // This requires the @tensorflow/tfjs-tflite library
        model = await tflite.loadTFLiteModel('recipe_model.tflite');
        console.log("Model loaded successfully");

        recommendBtn.disabled = false;
    } catch (error) {
        console.error("Initialization error:", error);
    }
}

function preprocess(text) {
    const tokens = text.toLowerCase().split(/[\s,]+/).filter(t => t.length > 0);
    const sequence = new Int32Array(maxLen).fill(0);

    // Pre-padding as in training
    let startIdx = maxLen - tokens.size; // Wait, tokens.length in JS
    startIdx = Math.max(0, maxLen - tokens.length);

    let tokenIdx = 0;
    for (let i = startIdx; i < maxLen; i++) {
        if (tokenIdx < tokens.length) {
            const word = tokens[tokenIdx];
            if (wordIndex[word]) {
                sequence[i] = wordIndex[word];
            }
            tokenIdx++;
        }
    }
    return sequence;
}

recommendBtn.addEventListener('click', async () => {
    const input = ingredientsInput.value.trim();
    if (!input) return;

    // UI Feedback
    btnText.textContent = 'Analyzing...';
    loader.style.display = 'block';
    recommendBtn.disabled = true;

    try {
        const sequence = preprocess(input);

        // Convert to tensor
        const inputTensor = tf.tensor(sequence, [1, maxLen], 'int32');

        // Run inference
        const outputTensor = model.predict(inputTensor);
        const results = await outputTensor.data();

        // Find max probability
        let maxIdx = 0;
        let maxProb = -1;
        for (let i = 0; i < results.length; i++) {
            if (results[i] > maxProb) {
                maxProb = results[i];
                maxIdx = i;
            }
        }

        const predictedRecipe = labels[maxIdx] || "Mystery Dish";

        // Update UI
        recipeTitle.textContent = predictedRecipe;
        resultSection.classList.remove('hidden');
        confidenceFill.style.width = `${Math.min(maxProb * 100 * 2, 100)}%`; // Scaled for visual impact

        // Clean up
        inputTensor.dispose();
        outputTensor.dispose();

    } catch (error) {
        console.error("Prediction error:", error);
        recipeTitle.textContent = "Error during recommendation";
    } finally {
        btnText.textContent = 'Discover Recipes';
        loader.style.display = 'none';
        recommendBtn.disabled = false;
    }
});

// Start initialization
recommendBtn.disabled = true;
init();
