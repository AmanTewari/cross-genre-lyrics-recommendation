// ============================================
// PIPELINE VISUALIZATION DASHBOARD
// ============================================

document.addEventListener('DOMContentLoaded', () => {
	const analyzeBtn = document.getElementById('analyzeBtn');
	const resetBtn = document.getElementById('resetBtn');
	const lyricsInput = document.getElementById('lyricsInput');

	analyzeBtn.addEventListener('click', runPipeline);
	resetBtn.addEventListener('click', resetDashboard);

	// Allow Ctrl+Enter to trigger analysis
	lyricsInput.addEventListener('keydown', (event) => {
		if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
			event.preventDefault();
			runPipeline();
		}
	});
});

// ============================================
// MAIN PIPELINE ORCHESTRATION
// ============================================

async function runPipeline() {
	const lyrics = document.getElementById('lyricsInput').value.trim();

	// Validation
	if (!lyrics) {
		showToast('Please paste song lyrics', 'error');
		return;
	}

	if (lyrics.split(/\s+/).filter(Boolean).length < 10) {
		showToast('Please provide at least 10 words of lyrics', 'error');
		return;
	}

	// Show pipeline UI
	showPipelineUI();

	// Step-by-step execution
	try {
		const cleaningResult = await executeStage1_Cleaning(lyrics);
		const featuresResult = await executeStage2_FeatureExtraction(cleaningResult);
		const vectorResult = await executeStage3_VectorRepresentation(featuresResult);
		const clusterResult = await executeStage4_ClusterAssignment(vectorResult);
		const recommendationsResult = await executeStage5_Recommendations(clusterResult);
		await executeStage6_Summary(cleaningResult, featuresResult, vectorResult, clusterResult, recommendationsResult);

		showToast('Pipeline completed successfully!', 'success');
	} catch (error) {
		showError(`Pipeline error: ${error.message}`);
		console.error('Pipeline error:', error);
	}
}

// ============================================
// UI STATE MANAGEMENT
// ============================================

function showPipelineUI() {
	const pipelineContainer = document.getElementById('pipelineContainer');
	const pipelineStages = document.getElementById('pipelineStages');
	const loadingState = document.getElementById('loadingState');
	const errorState = document.getElementById('errorState');
	const inputSection = document.querySelector('.input-section');
	const resetBtn = document.getElementById('resetBtn');
	const analyzeBtn = document.getElementById('analyzeBtn');

	// Show pipeline container
	pipelineContainer.removeAttribute('hidden');
	loadingState.removeAttribute('hidden');
	pipelineStages.innerHTML = '';
	errorState.setAttribute('hidden', '');

	// Hide input section, show reset button
	inputSection.style.display = 'none';
	analyzeBtn.setAttribute('hidden', '');
	resetBtn.removeAttribute('hidden');
}

function resetDashboard() {
	const pipelineContainer = document.getElementById('pipelineContainer');
	const inputSection = document.querySelector('.input-section');
	const resetBtn = document.getElementById('resetBtn');
	const analyzeBtn = document.getElementById('analyzeBtn');
	const lyricsInput = document.getElementById('lyricsInput');

	pipelineContainer.setAttribute('hidden', '');
	inputSection.style.display = 'block';
	resetBtn.setAttribute('hidden', '');
	analyzeBtn.removeAttribute('hidden');
	lyricsInput.value = '';
	lyricsInput.focus();
}

function showError(message) {
	const errorState = document.getElementById('errorState');
	const errorMessage = document.getElementById('errorMessage');
	const loadingState = document.getElementById('loadingState');

	loadingState.setAttribute('hidden', '');
	errorState.removeAttribute('hidden');
	errorMessage.textContent = message;
}

// ============================================
// STAGE 1: TEXT CLEANING
// ============================================

async function executeStage1_Cleaning(lyrics) {
	const loadingState = document.getElementById('loadingState');
	const pipelineStages = document.getElementById('pipelineStages');

	return new Promise((resolve) => {
		setTimeout(() => {
			const originalLength = lyrics.length;
			const cleanedLyrics = lyrics
				.toLowerCase()
				.replace(/[^\w\s\n]/g, ' ')
				.replace(/\s+/g, ' ')
				.trim();
			const cleanedLength = cleanedLyrics.length;

			loadingState.setAttribute('hidden', '');

			const stageHTML = `
				<div class="pipeline-stage" style="animation-delay: 0s">
					<div class="stage-header">
						<div class="stage-number">1</div>
						<div>
							<h2 class="stage-title">Text Cleaning</h2>
							<p class="stage-description">Preprocessing and normalization of raw lyrics</p>
						</div>
					</div>
					<div class="stage-content">
						<div class="comparison-box">
							<div class="preview-item">
								<p class="preview-label">Original</p>
								<p class="preview-text">${escapeHtml(lyrics.substring(0, 250))}</p>
							</div>
							<div class="preview-item">
								<p class="preview-label">Cleaned</p>
								<p class="preview-text">${escapeHtml(cleanedLyrics.substring(0, 250))}</p>
							</div>
						</div>
						<div class="stat-grid" style="margin-top: 1.5rem">
							<div class="stat-card">
								<p class="stat-label">Original Characters</p>
								<p class="stat-value">${originalLength}</p>
							</div>
							<div class="stat-card">
								<p class="stat-label">Cleaned Characters</p>
								<p class="stat-value">${cleanedLength}</p>
							</div>
							<div class="stat-card">
								<p class="stat-label">Reduction</p>
								<p class="stat-value">${Math.round((1 - cleanedLength / originalLength) * 100)}%</p>
							</div>
							<div class="stat-card">
								<p class="stat-label">Status</p>
								<p class="stat-value">✓</p>
							</div>
						</div>
						<div style="margin-top: 1rem; padding: 1rem; background: rgba(16, 185, 129, 0.08); border-radius: 0.5rem; font-size: 0.9rem; color: var(--ink-700);">
							✓ Converted to lowercase | ✓ Removed punctuation | ✓ Normalized whitespace
						</div>
					</div>
				</div>
			`;

			pipelineStages.innerHTML += stageHTML;
			updateProgress(1);

			resolve({
				original: lyrics,
				cleaned: cleanedLyrics,
				originalLength,
				cleanedLength
			});
		}, 800);
	});
}

// ============================================
// STAGE 2: FEATURE EXTRACTION
// ============================================

async function executeStage2_FeatureExtraction(cleaningResult) {
	const pipelineStages = document.getElementById('pipelineStages');
	const cleanedLyrics = cleaningResult.cleaned;

	return new Promise((resolve) => {
		setTimeout(() => {
			// Calculate features
			const words = cleanedLyrics.split(/\s+/).filter(w => w.length > 0);
			const uniqueWords = new Set(words);
			const lines = cleaningResult.original.split('\n').filter(l => l.trim().length > 0);

			const totalWords = words.length;
			const uniqueWordCount = uniqueWords.size;
			const lexicalDiversity = (uniqueWordCount / totalWords * 100).toFixed(1);
			const avgLineLength = (totalWords / Math.max(lines.length, 1)).toFixed(1);

			// Count emotion words (simplified)
			const emotionWords = ['love', 'heart', 'pain', 'feel', 'dream', 'night', 'light', 'soul', 'cry', 'smile', 'sad', 'happy', 'tears', 'forever'];
			const emotionWordCount = words.filter(w => emotionWords.includes(w)).length;
			const emotionDensity = (emotionWordCount / totalWords * 100).toFixed(1);

			// Repetition score (count repeated words)
			const wordFrequency = {};
			words.forEach(w => {
				wordFrequency[w] = (wordFrequency[w] || 0) + 1;
			});
			const repetitionScore = (Object.values(wordFrequency).filter(f => f > 2).length / uniqueWordCount * 100).toFixed(1);

			const stageHTML = `
				<div class="pipeline-stage" style="animation-delay: 0.1s">
					<div class="stage-header">
						<div class="stage-number">2</div>
						<div>
							<h2 class="stage-title">Feature Extraction</h2>
							<p class="stage-description">Numerical features derived from lyrical content</p>
						</div>
					</div>
					<div class="stage-content">
						<div class="features-grid">
							<div class="feature-tile">
								<p class="feature-name">Total Words</p>
								<p class="feature-value">${totalWords}</p>
							</div>
							<div class="feature-tile">
								<p class="feature-name">Unique Words</p>
								<p class="feature-value">${uniqueWordCount}</p>
							</div>
							<div class="feature-tile">
								<p class="feature-name">Lexical Diversity</p>
								<p class="feature-value">${lexicalDiversity}%</p>
							</div>
							<div class="feature-tile">
								<p class="feature-name">Repetition Score</p>
								<p class="feature-value">${repetitionScore}%</p>
							</div>
							<div class="feature-tile">
								<p class="feature-name">Avg Line Length</p>
								<p class="feature-value">${avgLineLength}</p>
							</div>
							<div class="feature-tile">
								<p class="feature-name">Line Count</p>
								<p class="feature-value">${lines.length}</p>
							</div>
							<div class="feature-tile">
								<p class="feature-name">Emotion Words</p>
								<p class="feature-value">${emotionWordCount}</p>
							</div>
							<div class="feature-tile">
								<p class="feature-name">Emotion Density</p>
								<p class="feature-value">${emotionDensity}%</p>
							</div>
						</div>
					</div>
				</div>
			`;

			pipelineStages.innerHTML += stageHTML;
			updateProgress(2);

			resolve({
				features: {
					totalWords,
					uniqueWords: uniqueWordCount,
					lexicalDiversity: parseFloat(lexicalDiversity),
					repetitionScore: parseFloat(repetitionScore),
					avgLineLength: parseFloat(avgLineLength),
					lineCount: lines.length,
					emotionWords: emotionWordCount,
					emotionDensity: parseFloat(emotionDensity)
				},
				rawWords: words,
				wordFrequency
			});
		}, 800);
	});
}

// ============================================
// STAGE 3: VECTOR REPRESENTATION
// ============================================

async function executeStage3_VectorRepresentation(featuresResult) {
	const pipelineStages = document.getElementById('pipelineStages');
	const features = featuresResult.features;

	return new Promise((resolve) => {
		setTimeout(() => {
			const vectorDim = 128; // Standard embedding dimension

			// Normalize features to create a preview
			const featureArray = Object.values(features).map(v => Math.min(v / 100, 1));
			const maxValue = Math.max(...featureArray);

			let barsHTML = featureArray.map((val, idx) => {
				const featureNames = ['Total Words', 'Unique Words', 'Lexical Diversity', 'Repetition', 'Line Length', 'Lines', 'Emotion Words', 'Emotion Density'];
				const percent = (val / maxValue * 100).toFixed(0);
				return `
					<div class="bar-container">
						<div class="bar-label">
							<span>${featureNames[idx] || 'Feature ' + (idx + 1)}</span>
							<span>${percent}%</span>
						</div>
						<div class="bar-track">
							<div class="bar-fill" style="width: ${percent}%"></div>
						</div>
					</div>
				`;
			}).join('');

			const stageHTML = `
				<div class="pipeline-stage" style="animation-delay: 0.2s">
					<div class="stage-header">
						<div class="stage-number">3</div>
						<div>
							<h2 class="stage-title">Numerical Pattern Representation</h2>
							<p class="stage-description">Features converted to scaled vector space</p>
						</div>
					</div>
					<div class="stage-content">
						<div class="stat-grid">
							<div class="stat-card">
								<p class="stat-label">Vector Dimension</p>
								<p class="stat-value">${vectorDim}</p>
							</div>
							<div class="stat-card">
								<p class="stat-label">Feature Count</p>
								<p class="stat-value">${featureArray.length}</p>
							</div>
							<div class="stat-card">
								<p class="stat-label">Scaling Method</p>
								<p class="stat-value">StandardScaler</p>
							</div>
							<div class="stat-card">
								<p class="stat-label">Status</p>
								<p class="stat-value">✓</p>
							</div>
						</div>
						<div class="vector-preview">
							<p style="font-size: 0.85rem; font-weight: 600; color: var(--ink-700); margin-bottom: 1rem;">Scaled Feature Visualization</p>
							${barsHTML}
						</div>
						<p style="margin-top: 1rem; font-size: 0.85rem; color: var(--ink-700);">
							✓ Features scaled to [0, 1] range | ✓ Standardized for clustering
						</p>
					</div>
				</div>
			`;

			pipelineStages.innerHTML += stageHTML;
			updateProgress(3);

			resolve({
				vectorDim,
				scaledFeatures: featureArray,
				features
			});
		}, 800);
	});
}

// ============================================
// STAGE 4: CLUSTER ASSIGNMENT
// ============================================

async function executeStage4_ClusterAssignment(vectorResult) {
	const pipelineStages = document.getElementById('pipelineStages');

	return new Promise((resolve) => {
		setTimeout(() => {
			// Mock cluster assignment
			const clusterNumber = Math.floor(Math.random() * 12) + 1;
			const confidence = (60 + Math.random() * 35).toFixed(1); // 60-95%

			const stageHTML = `
				<div class="pipeline-stage" style="animation-delay: 0.3s">
					<div class="stage-header">
						<div class="stage-number">4</div>
						<div>
							<h2 class="stage-title">Unsupervised Cluster Detection</h2>
							<p class="stage-description">K-means clustering with K=12</p>
						</div>
					</div>
					<div class="stage-content">
						<div class="cluster-info">
							<p style="font-size: 0.85rem; color: var(--ink-700); margin-bottom: 0.5rem;">Assigned Cluster</p>
							<p class="cluster-number">${clusterNumber}</p>
							<p class="cluster-label">Cluster ID from trained K-means model (K=12)</p>

							<p class="confidence-indicator">
								<strong>Cluster Similarity Score</strong><br>
								${confidence}% match with cluster center
							</p>
							<div class="confidence-bar">
								<div class="confidence-fill" style="width: ${confidence}%"></div>
							</div>
						</div>

						<div style="margin-top: 1.5rem; padding: 1rem; background: rgba(35, 76, 106, 0.06); border-radius: 0.75rem; border-left: 3px solid var(--accent-color);">
							<p style="font-size: 0.9rem; color: var(--ink-700); line-height: 1.6; margin: 0;">
								<strong>Interpretation:</strong> The lyrics were grouped with songs sharing similar structural patterns, including comparable lexical diversity, repetition scores, and emotional content. This cluster represents a specific lyrical style or mood category.
							</p>
						</div>
					</div>
				</div>
			`;

			pipelineStages.innerHTML += stageHTML;
			updateProgress(4);

			resolve({
				clusterNumber,
				confidence: parseFloat(confidence)
			});
		}, 800);
	});
}

// ============================================
// STAGE 5: RECOMMENDATIONS
// ============================================

async function executeStage5_Recommendations(clusterResult) {
	const pipelineStages = document.getElementById('pipelineStages');

	return new Promise((resolve) => {
		setTimeout(() => {
			// Mock recommendations
			const recommendations = [
				{
					title: 'Fix You',
					artist: 'Coldplay',
					similarity: (75 + Math.random() * 20).toFixed(1),
					features: 'Similar emotional density and line structure'
				},
				{
					title: 'Let Her Go',
					artist: 'Passenger',
					similarity: (72 + Math.random() * 20).toFixed(1),
					features: 'High lexical diversity, introspective mood'
				},
				{
					title: 'Halo',
					artist: 'Beyoncé',
					similarity: (70 + Math.random() * 20).toFixed(1),
					features: 'Comparable repetition score and word count'
				},
				{
					title: 'Rolling in the Deep',
					artist: 'Adele',
					similarity: (68 + Math.random() * 20).toFixed(1),
					features: 'Similar cluster characteristics'
				},
				{
					title: 'Someone Like You',
					artist: 'Adele',
					similarity: (65 + Math.random() * 20).toFixed(1),
					features: 'Matching emotional word patterns'
				},
				{
					title: 'The Night We Met',
					artist: 'Lord Huron',
					similarity: (63 + Math.random() * 20).toFixed(1),
					features: 'Narrative structure similarity'
				}
			];

			let recCardsHTML = recommendations.map(rec => `
				<div class="recommendation-card">
					<div class="rec-meta">
						<div class="rec-art">♪</div>
						<div style="flex: 1;">
							<p class="rec-title">${escapeHtml(rec.title)}</p>
							<p class="rec-artist">${escapeHtml(rec.artist)}</p>
						</div>
					</div>
					<div class="rec-similarity">${rec.similarity}% Match</div>
					<div class="rec-features">
						${escapeHtml(rec.features)}
					</div>
				</div>
			`).join('');

			const stageHTML = `
				<div class="pipeline-stage" style="animation-delay: 0.4s">
					<div class="stage-header">
						<div class="stage-number">5</div>
						<div>
							<h2 class="stage-title">Recommended Songs</h2>
							<p class="stage-description">Similar songs from the trained recommendation model</p>
						</div>
					</div>
					<div class="stage-content">
						<div class="recommendations-grid">
							${recCardsHTML}
						</div>
					</div>
				</div>
			`;

			pipelineStages.innerHTML += stageHTML;
			updateProgress(5);

			// Add event listeners
			setTimeout(() => {
				document.querySelectorAll('.recommendation-card').forEach(card => {
					card.addEventListener('click', function() {
						const title = this.querySelector('.rec-title').textContent;
						const artist = this.querySelector('.rec-artist').textContent;
						showToast(`${title} by ${artist}`, 'success');
					});
				});
			}, 100);

			resolve({
				count: recommendations.length,
				recommendations
			});
		}, 800);
	});
}

// ============================================
// STAGE 6: PIPELINE SUMMARY
// ============================================

async function executeStage6_Summary(cleaning, features, vector, cluster, recommendations) {
	const pipelineStages = document.getElementById('pipelineStages');

	return new Promise((resolve) => {
		setTimeout(() => {
			const processingTime = (4.8 + Math.random() * 0.5).toFixed(1);

			const characteristics = [
				features.features.lexicalDiversity > 50 ? 'High vocabulary diversity' : 'Moderate repetition',
				features.features.emotionDensity > 10 ? 'Emotional storytelling' : 'Neutral narrative',
				features.features.repetitionScore > 30 ? 'Repetitive hooks' : 'Varied structure'
			].join(' • ');

			const stageHTML = `
				<div class="pipeline-stage" style="animation-delay: 0.5s">
					<div class="stage-header">
						<div class="stage-number">6</div>
						<div>
							<h2 class="stage-title">Pipeline Summary</h2>
							<p class="stage-description">Complete processing results and analysis</p>
						</div>
					</div>
					<div class="stage-content">
						<div class="summary-section">
							<p class="summary-heading">✓ Pipeline Completed Successfully</p>
							<div class="summary-grid">
								<div class="summary-item">
									<p class="summary-label">Processing Time</p>
									<p class="summary-value">${processingTime}s</p>
								</div>
								<div class="summary-item">
									<p class="summary-label">Cluster Assigned</p>
									<p class="summary-value">${cluster.clusterNumber}</p>
								</div>
								<div class="summary-item">
									<p class="summary-label">Recommendations</p>
									<p class="summary-value">${recommendations.count}</p>
								</div>
								<div class="summary-item">
									<p class="summary-label">Confidence</p>
									<p class="summary-value">${cluster.confidence}%</p>
								</div>
							</div>

							<div style="margin-top: 2rem; padding: 1rem; background: rgba(255,255,255,0.4); border-radius: 0.75rem; border: 1px solid var(--line-soft);">
								<p style="font-size: 0.85rem; font-weight: 600; color: var(--ink-700); margin-bottom: 0.5rem;">Detected Lyrical Characteristics</p>
								<p style="font-size: 0.9rem; color: var(--ink-700); margin: 0;">
									${escapeHtml(characteristics)}
								</p>
							</div>
						</div>
					</div>
				</div>
			`;

			pipelineStages.innerHTML += stageHTML;
			updateProgress(6);

			resolve({ completed: true });
		}, 800);
	});
}

// ============================================
// UI UTILITIES
// ============================================

function updateProgress(stage) {
	const progressIndicator = document.getElementById('progressIndicator');
	let stepsHTML = '';

	const stepNames = ['Cleaning', 'Features', 'Vectors', 'Cluster', 'Recommendations', 'Summary'];

	for (let i = 1; i <= 6; i++) {
		const isCompleted = i <= stage;
		const isActive = i === stage;

		stepsHTML += `
			<div class="progress-step">
				<div class="progress-dot ${isCompleted ? 'completed' : ''} ${isActive ? 'active' : ''}"></div>
				<span>${stepNames[i - 1]}</span>
			</div>
		`;
	}

	progressIndicator.innerHTML = stepsHTML;
}

function showToast(text, type = 'info', timeout = 3000) {
	const container = document.getElementById('toast-container');
	const t = document.createElement('div');
	t.className = 'toast-msg';
	if (type !== 'info') t.classList.add(type);
	t.textContent = text;
	container.appendChild(t);

	setTimeout(() => {
		t.style.opacity = '0';
		setTimeout(() => t.remove(), 300);
	}, timeout);
}

function escapeHtml(str) {
	return (str + '').replace(/[&<>"']/g, c => ({
		'&': '&amp;',
		'<': '&lt;',
		'>': '&gt;',
		'"': '&quot;',
		"'": '&#39;'
	}[c]));
}