<script lang="ts">
	import type { Model, CacheStats } from '$lib/types';

	interface Props {
		models: Model[];
		selectedModel: string;
		useRag: boolean;
		topK: number;
		cacheStats: CacheStats;
		ragDocs: number;
		onModelChange: (id: string) => void;
		onRagToggle: () => void;
		onTopKChange: (val: number) => void;
		onClearCache: () => void;
	}

	let {
		models,
		selectedModel,
		useRag,
		topK,
		cacheStats,
		ragDocs,
		onModelChange,
		onRagToggle,
		onTopKChange,
		onClearCache
	}: Props = $props();
</script>

<div class="h-full flex flex-col" style="background: var(--bg-secondary);">
	<!-- Logo -->
	<div class="p-5 border-b" style="border-color: var(--border);">
		<div class="flex items-center gap-3">
			<div
				class="w-9 h-9 rounded-lg flex items-center justify-center text-lg font-bold"
				style="background: var(--accent); color: white;"
			>
				N
			</div>
			<div>
				<h1 class="text-sm font-bold" style="color: var(--text-primary);">NordicPay AI</h1>
				<p class="text-[11px]" style="color: var(--text-muted);">Banking Assistant</p>
			</div>
		</div>
	</div>

	<div class="flex-1 overflow-y-auto p-4 space-y-6">
		<!-- Model selector -->
		<section>
			<span
				class="block text-[10px] font-semibold uppercase tracking-widest mb-2"
				style="color: var(--text-muted);"
			>
				Model
        </span>
			<select
				value={selectedModel}
				onchange={(e) => onModelChange((e.target as HTMLSelectElement).value)}
				class="w-full px-3 py-2.5 rounded-lg text-sm outline-none cursor-pointer"
				style="background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border);"
			>
				{#each models as m}
					<option value={m.id}>{m.name}</option>
				{/each}
			</select>
			<p class="text-[10px] mt-1.5" style="color: var(--text-muted);">
				{#if models.find((m) => m.id === selectedModel)?.type === 'local'}
					⚠️ Local model — slow on CPU
				{:else}
					⚡ API model — fast responses
				{/if}
			</p>
		</section>

		<!-- RAG -->
		<section>
			<span
				class="block text-[10px] font-semibold uppercase tracking-widest mb-2"
				style="color: var(--text-muted);"
			>
				Knowledge Base
        </span>
			<button
				onclick={onRagToggle}
				class="w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm"
				style="background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border);"
			>
				<span>RAG Retrieval</span>
				<span
					class="w-10 h-5 rounded-full relative transition-all duration-200"
					style="background: {useRag ? 'var(--accent)' : 'var(--bg-hover)'};"
				>
					<span
						class="absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all duration-200"
						style="left: {useRag ? '22px' : '2px'};"
					></span>
				</span>
			</button>

			{#if useRag}
				<div class="mt-3 px-1">
					<div class="flex justify-between text-[11px] mb-1">
						<span style="color: var(--text-muted);">Context chunks</span>
						<span style="color: var(--accent-light);">{topK}</span>
					</div>
					<input
						type="range"
						min="1"
						max="5"
						value={topK}
						oninput={(e) => onTopKChange(Number((e.target as HTMLInputElement).value))}
						class="w-full accent-[#6c5ce7]"
					/>
				</div>
			{/if}
		</section>

		<!-- Stats -->
		<section>
			<span
				class="block text-[10px] font-semibold uppercase tracking-widest mb-2"
				style="color: var(--text-muted);"
			>
				Stats
        </span>
			<div class="space-y-1.5">
				<div
					class="flex justify-between text-xs px-3 py-2 rounded-lg"
					style="background: var(--bg-tertiary);"
				>
					<span style="color: var(--text-secondary);">Cached responses</span>
					<span style="color: var(--success);">{cacheStats.valid}</span>
				</div>
				<div
					class="flex justify-between text-xs px-3 py-2 rounded-lg"
					style="background: var(--bg-tertiary);"
				>
					<span style="color: var(--text-secondary);">RAG documents</span>
					<span style="color: var(--accent-light);">{ragDocs}</span>
				</div>
			</div>
		</section>

		<!-- Actions -->
		<section>
			<button
				onclick={onClearCache}
				class="w-full text-xs py-2.5 rounded-lg border transition-all duration-200 hover:brightness-125"
				style="border-color: var(--border); color: var(--text-secondary); background: var(--bg-tertiary);"
			>
				Clear Cache
			</button>
		</section>
	</div>
</div>