<template>
    <nav>
        <template v-if="isLoggedIn">
            <NavbarLogged />
        </template>
        <template v-else>
            <NavbarGuest />
        </template>
    </nav>
</template>

<script setup>
import { defineProps } from 'vue';
import NavbarLogged from './NavbarLogged.vue';
import NavbarGuest from './NavbarGuest.vue';

const props = defineProps({
    isLoggedIn: Boolean
});
</script>
