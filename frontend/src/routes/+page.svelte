<script lang="ts">
	import { onMount } from 'svelte';
	import type { Message, Model, CacheStats } from '$lib/types';
	import { sendMessage, getModels, getCacheStats, clearCache, getRagStats } from '$lib/api';
	import Sidebar from '$lib/components/Sidebar.svelte';
	import Chat from '$lib/components/Chat.svelte';

	let messages: Message[] = $state([]);
	let loading = $state(false);
	let error = $state('');

	let models: Model[] = $state([]);
	let selectedModel = $state('openai');
	let useRag = $state(true);
	let topK = $state(3);
	let cacheStats: CacheStats = $state({ total: 0, valid: 0 });
	let ragDocs = $state(0);
	let sidebarOpen = $state(false);

	onMount(async () => {
		try {
			const m = await getModels();
			models = m.models;
			if (models.length > 0) selectedModel = models[0].id;

			cacheStats = await getCacheStats();
			const r = await getRagStats();
			ragDocs = r.documents;
		} catch {
			error = 'Backend not running. Start with: uvicorn app.main:app --reload';
		}
	});

	async function handleSend(text: string) {
		if (!text || loading) return;
		error = '';

		messages = [...messages, { role: 'user', content: text }];
		loading = true;

		try {
			const res = await sendMessage(text, selectedModel, useRag, topK);

			//Calculate confidence from source score 
			const avgScore = res.sources.length > 0
			   ? res.sources.reduce((sum , s) => sum + s.score, 0) / res.sources.length
			   : 0;
			const confidence = Math.min(Math.round(avgScore * 100 + 20), 100)
			messages = [
				...messages,
				{
					role: 'assistant',
					content: res.answer,
					meta: {
						model: res.model_used,
						cached: res.from_cache,
						latency: res.latency_ms,
						sources: res.sources,
						reasoning: res.reasoning || [],
						confidence: confidence
					}
				}
			];
			cacheStats = await getCacheStats();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Something went wrong';
		} finally {
			loading = false;
		}
	}

	async function handleClearCache() {
		await clearCache();
		cacheStats = await getCacheStats();
	}
</script>

<div class="flex h-screen overflow-hidden">
	<!-- Desktop sidebar -->
	<div class="w-72 flex-shrink-0 hidden md:block border-r" style="border-color: var(--border);">
		<Sidebar
			{models}
			{selectedModel}
			{useRag}
			{topK}
			{cacheStats}
			{ragDocs}
			onModelChange={(id) => (selectedModel = id)}
			onRagToggle={() => (useRag = !useRag)}
			onTopKChange={(val) => (topK = val)}
			onClearCache={handleClearCache}
		/>
	</div>

	<!-- Mobile sidebar overlay -->
	{#if sidebarOpen}
		<button
			class="fixed inset-0 bg-black/60 z-40 md:hidden"
			onclick={() => (sidebarOpen = false)}
            aria-label="Close sidebar"
		></button>
		<div class="fixed left-0 top-0 bottom-0 w-72 z-50 md:hidden">
			<Sidebar
				{models}
				{selectedModel}
				{useRag}
				{topK}
				{cacheStats}
				{ragDocs}
				onModelChange={(id) => (selectedModel = id)}
				onRagToggle={() => (useRag = !useRag)}
				onTopKChange={(val) => (topK = val)}
				onClearCache={handleClearCache}
			/>
		</div>
	{/if}

	<!-- Main -->
	<div class="flex-1 flex flex-col min-w-0">
		<!-- Mobile header -->
		<div
			class="md:hidden flex items-center gap-3 px-4 py-3 border-b"
			style="border-color: var(--border); background: var(--bg-secondary);"
		>
			<button
				onclick={() => (sidebarOpen = !sidebarOpen)}
				class="text-lg"
				style="color: var(--text-primary);"
			>
				☰
			</button>
			<span class="font-semibold text-sm" style="color: var(--text-primary);">NordicPay AI</span>
		</div>

		<Chat
			{messages}
			{models}
			{loading}
			{error}
			onSend={handleSend}
			onSuggestion={handleSend}
		/>
	</div>
</div>