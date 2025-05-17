<template>
    <ul class="flex space-x-4">
        <li><a href="/dashboard" class="text-blue-600 hover:underline">Dashboard</a></li>
        <li><a href="/profile" class="text-blue-600 hover:underline">Perfil</a></li>
        <li>
            <form method="POST" action="/logout">
                <button type="submit" class="text-red-600 hover:underline">Sair</button>
            </form>
        </li>
    </ul>
</template>

<script setup>
// Aqui pode ter lógica para pegar dados do usuário se quiser mostrar nome, etc.
// Por enquanto, simples.
</script>

<style scoped>
/* Estilos básicos, use Tailwind ou seus estilos */
</style>
