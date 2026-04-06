export interface Model {
	id: string;
	name: string;
	type: string;
	ready: boolean;
}

export interface Source {
	text: string;
	score: number;
	source: string;
}

export interface ReasoningStep {
	step: number;
	action: string;
	detail: string;
}

export interface MessageMeta {
	model: string;
	cached: boolean;
	latency: number;
	sources: Source[];
	reasoning?: ReasoningStep[];
	confidence?: number;
}

export interface Message {
	role: 'user' | 'assistant';
	content: string;
	meta?: MessageMeta;
}

export interface ChatResponse {
	answer: string;
	model_used: string;
	from_cache: boolean;
	sources: Source[];
	reasoning?: ReasoningStep[];
	latency_ms: number;
}

export interface ModelsResponse {
	models: Model[];
}

export interface CacheStats {
	total: number;
	valid: number;
}

export interface RagStats {
	documents: number;
}