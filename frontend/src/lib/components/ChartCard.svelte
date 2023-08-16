<script lang="ts">
    export let title: string;
</script>

<div class="card w-full sm:w-96 bg-white shadow-xl">
    <figure class="p-2">
        <slot />
    </figure>
    <div class="card-body">
        <h2 class="card-title">{title}</h2>
    </div>
</div>