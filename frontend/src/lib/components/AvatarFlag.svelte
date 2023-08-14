<script lang="ts">
	export let flag: string;
	export let alt: string = flag;
	export let size: string = 'w-10';

</script>

<div class="avatar">
	<div class={`${size} rounded-full`}>
		<img src={`/flags/${flag ? flag.toLowerCase() : "xxx"}.svg`} {alt} />
	</div>
</div>
