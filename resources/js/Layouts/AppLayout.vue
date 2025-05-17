<template>
    <div class="min-h-screen flex flex-col">
        <Header />
        <Navbar :is-logged-in="isLoggedIn" />
        <main class="flex-grow container mx-auto px-4 py-6">
            <slot />
        </main>
        <Footer />
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { usePage } from '@inertiajs/vue3';

import Header from '@/Components/Header.vue';
import Navbar from '@/Components/Navbar.vue';
import Footer from '@/Components/Footer.vue';

const page = usePage();

// Ajuste para garantir que 'auth' exista antes de acessar 'user'
const isLoggedIn = computed(() => !!(page.props.value?.auth?.user));
</script>
