<script lang="ts">
    import type { Message, Model } from '$lib/types';
	import MessageBubble from './MessageBubble.svelte';

	interface Props {
		messages: Message[];
		models: Model[];
		loading: boolean;
		error: string;
		onSend: (text: string) => void;
		onSuggestion: (text: string) => void;
	}

	let { messages, models, loading, error, onSend, onSuggestion }: Props = $props();

	let input = $state('');
	let chatContainer: HTMLDivElement | null = $state(null);

	const suggestions = [
		'What accounts do you offer?',
		'How do I freeze my card?',
		'What are the loan rates?',
		'Is my data encrypted?'
	];

	function send() {
		if (!input.trim() || loading) return;
		onSend(input.trim());
		input = '';
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' && !e.shiftKey) {
			e.preventDefault();
			send();
		}
	}

	$effect(() => {
		if (messages.length && chatContainer) {
			// Scroll to bottom on new message
			chatContainer.scrollTop = chatContainer.scrollHeight;
		}
	});
</script>

<div class="flex-1 flex flex-col min-w-0 h-full">
	<!-- Messages -->
	<div bind:this={chatContainer} class="flex-1 overflow-y-auto px-4 py-6 space-y-4">
		{#if messages.length === 0}
			<div class="flex items-center justify-center h-full">
				<div class="text-center space-y-5">
					<div
						class="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-bold mx-auto"
						style="background: var(--accent); color: white;"
					>
						N
					</div>
					<div>
						<h2 class="text-xl font-bold" style="color: var(--text-primary);">
							NordicPay Assistant
						</h2>
						<p class="text-sm mt-1 max-w-sm mx-auto" style="color: var(--text-muted);">
							Ask about accounts, loans, cards, fees, security, or anything NordicPay.
						</p>
					</div>
					<div class="flex flex-wrap gap-2 justify-center pt-2">
						{#each suggestions as q}
							<button
								onclick={() => onSuggestion(q)}
								class="text-xs px-4 py-2 rounded-full border transition-all duration-200 hover:brightness-125"
								style="border-color: var(--border); color: var(--text-secondary); background: var(--bg-tertiary);"
							>
								{q}
							</button>
						{/each}
					</div>
				</div>
			</div>
		{/if}

		{#each messages as msg}
			<div class="max-w-2xl mx-auto w-full">
				<MessageBubble message={msg} {models} />
			</div>
		{/each}

		{#if loading}
	<div class="max-w-2xl mx-auto w-full">
		<div class="flex justify-start">
			<div
				class="px-5 py-4 rounded-2xl rounded-bl-sm"
				style="background: var(--bot-bubble); border: 1px solid var(--border);"
			>
				<div class="space-y-2">
					<div class="flex items-center gap-2">
						<div class="flex gap-1.5">
							{#each [0, 1, 2] as i}
								<span
								  class="w-2 h-2 rounded-full animate-bounce"
								  style="background: var(--accent); animation-delay: {i * 0.15}s;"
								></span>
							{/each}
						</div>
						<span class="text-sm" style="color: var(--text-muted);">Thinking...</span>
					</div>
					<div class="text-xs space-y-1" style="color: var(--text-muted);">
						<div class="animate-pulse">Analyzing your question...</div>
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}

		{#if error}
			<div class="max-w-2xl mx-auto w-full">
				<div
					class="text-sm px-4 py-3 rounded-lg"
					style="background: #ff6b6b10; color: var(--error); border: 1px solid #ff6b6b25;"
				>
					{error}
				</div>
			</div>
		{/if}
	</div>

	<!-- Input bar -->
	<div class="p-4 border-t" style="border-color: var(--border); background: var(--bg-secondary);">
		<div class="max-w-2xl mx-auto flex gap-3">
			<textarea
				bind:value={input}
				onkeydown={handleKeydown}
				placeholder="Ask about NordicPay..."
				rows={1}
				disabled={loading}
				class="flex-1 resize-none px-4 py-3 rounded-xl text-sm outline-none placeholder:opacity-40"
				style="background: var(--bg-tertiary); color: var(--text-primary); border: 1px solid var(--border);"
			></textarea>
			<button
				onclick={send}
				disabled={loading || !input.trim()}
				class="px-5 py-3 rounded-xl text-sm font-semibold transition-all duration-200"
				style="background: var(--accent); color: white; opacity: {loading || !input.trim()
					? 0.4
					: 1};"
			>
				{#if loading}
					...
				{:else}
					Send
				{/if}
			</button>
		</div>
	</div>
</div>