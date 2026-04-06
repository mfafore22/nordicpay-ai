import type { ChatResponse, ModelsResponse, CacheStats, RagStats } from './types.ts';

const BASE = '/api';

export async function sendMessage(
	question: string,
	modelId: string,
	useRag: boolean,
	topK: number
): Promise<ChatResponse> {
	const res = await fetch(`${BASE}/chat`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify({
			question,
			model_id: modelId,
			use_rag: useRag,
			top_k: topK
		})
	});
	if (!res.ok) {
		const err = await res.json();
		throw new Error(err.detail || 'Request failed');
	}
	return res.json();
}

export async function getModels(): Promise<ModelsResponse> {
	const res = await fetch(`${BASE}/models`);
	if (!res.ok) throw new Error('Failed to fetch models');
	return res.json();
}

export async function getCacheStats(): Promise<CacheStats> {
	const res = await fetch(`${BASE}/cache/stats`);
	if (!res.ok) throw new Error('Failed to fetch cache stats');
	return res.json();
}

export async function clearCache(): Promise<void> {
	await fetch(`${BASE}/cache/clear`, { method: 'POST' });
}

export async function getRagStats(): Promise<RagStats> {
	const res = await fetch(`${BASE}/rag/stats`);
	if (!res.ok) throw new Error('Failed to fetch RAG stats');
	return res.json();
}

export async function rebuildRag(): Promise<void> {
	await fetch(`${BASE}/rag/rebuild`, { method: 'POST' });
}