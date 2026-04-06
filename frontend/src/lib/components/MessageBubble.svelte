<script lang="ts">
	import type { Message, Model } from '$lib/types';

	interface Props {
		message: Message;
		models: Model[];
	}

	let { message, models }: Props = $props();

	function getModelName(id: string): string {
		const m = models.find((m) => m.id === id);
		return m ? m.name : id;
	}

	function getConfidenceColor(confidence: number): string {
		if (confidence >= 70) return 'var(--success)';
		if (confidence >= 40) return '#f59e0b';
		return 'var(--error)';
	}

	function getConfidenceLabel(confidence: number): string {
		if (confidence >= 70) return 'High';
		if (confidence >= 40) return 'Medium';
		return 'Low';
	}

	let sourcesOpen = $state(false);
	let reasoningOpen = $state(false);
</script>

{#if message.role === 'user'}
	<div class="flex justify-end">
		<div
			class="px-4 py-3 rounded-2xl rounded-br-sm max-w-lg text-sm leading-relaxed"
			style="background: var(--accent-dim); color: var(--text-primary);"
		>
			{message.content}
		</div>
	</div>
{:else}
	<div class="flex justify-start">
		<div class="max-w-lg">
			<div
				class="px-4 py-3 rounded-2xl rounded-bl-sm text-sm leading-relaxed whitespace-pre-wrap"
				style="background: var(--bot-bubble); color: var(--text-primary); border: 1px solid var(--border);"
			>
				{message.content}
			</div>

			{#if message.meta}
				<div class="flex items-center gap-2 mt-1.5 ml-1 flex-wrap">
					<span
						class="text-[10px] px-2 py-0.5 rounded-full"
						style="background: var(--bg-tertiary); color: var(--accent-light);"
					>
						{getModelName(message.meta.model)}
					</span>

					{#if message.meta.confidence !== undefined}
						<span
							class="text-[10px] px-2 py-0.5 rounded-full"
							style="background: var(--bg-tertiary); color: {getConfidenceColor(message.meta.confidence)};"
						>
							{getConfidenceLabel(message.meta.confidence)} ({message.meta.confidence}%)
						</span>
					{/if}

					{#if message.meta.cached}
						<span
							class="text-[10px] px-2 py-0.5 rounded-full"
							style="background: #00d2a015; color: var(--success);"
						>
							cached
						</span>
					{:else}
						<span
							class="text-[10px] px-2 py-0.5 rounded-full"
							style="background: var(--bg-tertiary); color: var(--text-muted);"
						>
							{message.meta.latency}ms
						</span>
					{/if}

					{#if message.meta.reasoning && message.meta.reasoning.length > 0}
						<button
							onclick={() => (reasoningOpen = !reasoningOpen)}
							class="text-[10px] px-2 py-0.5 rounded-full cursor-pointer transition-colors"
							style="background: var(--bg-tertiary); color: var(--text-muted);"
						>
							{reasoningOpen ? 'Hide' : 'Show'} reasoning
						</button>
					{/if}

					{#if message.meta.sources.length > 0}
						<button
							onclick={() => (sourcesOpen = !sourcesOpen)}
							class="text-[10px] px-2 py-0.5 rounded-full cursor-pointer transition-colors"
							style="background: var(--bg-tertiary); color: var(--text-muted);"
						>
							{sourcesOpen ? 'Hide' : 'Show'} {message.meta.sources.length} sources
						</button>
					{/if}
				</div>

				{#if reasoningOpen && message.meta.reasoning && message.meta.reasoning.length > 0}
					<div class="mt-2 ml-1 space-y-1">
						<div class="text-[10px] font-semibold mb-1" style="color: var(--text-muted);">
							Reasoning Steps:
						</div>
						{#each message.meta.reasoning as r}
							<div
								class="text-[11px] px-3 py-2 rounded-lg flex items-start gap-2"
								style="background: var(--bg-tertiary); color: var(--text-secondary);"
							>
								<span
									class="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0"
									style="background: var(--accent); color: white;"
								>
									{r.step}
								</span>
								<div>
									<span style="color: var(--accent-light); font-weight: 600;">{r.action}</span>
									<span style="color: var(--text-muted);"> - {r.detail}</span>
								</div>
							</div>
						{/each}
					</div>
				{/if}

				{#if sourcesOpen && message.meta.sources.length > 0}
					<div class="mt-2 ml-1 space-y-1">
						<div class="text-[10px] font-semibold mb-1" style="color: var(--text-muted);">
							Sources:
						</div>
						{#each message.meta.sources as s}
							<div
								class="text-[11px] px-3 py-2 rounded-lg"
								style="background: var(--bg-tertiary); color: var(--text-secondary);"
							>
								<span style="color: var(--accent-light); font-weight: 600;">
								  {(s.score * 100).toFixed(0)}%
								</span>
								{s.text.slice(0, 120)}...
							</div>
						{/each}
					</div>
				{/if}
			{/if}
		</div>
	</div>
{/if}