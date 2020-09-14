<template>
    <div class="tile">
        <div class="d-flex justify-content-between">
            <div>
                <div class="tile__title">{{title}}</div>
                <div class="tile__subtitle">{{subtitle}}</div>
            </div>
            <span class="tile__count">{{count}}</span>
        </div>

        <slot></slot>
    </div>
</template>


<script>
    export default {
        props: ["title", "subtitle", "count"],
        data() {
            return {};
        }
    };
</script>
