<template>
    <!--
        Some versions of IE and Edge don't fire input event on selection change,
        see https://caniuse.com/#feat=input-event.
        Triggering $emit on change instead of input event
        to make it work for browsers mentioned above.
    -->
    <select
        :disabled="disabled"
        v-bind:value="value"
        v-on:change="$emit('input', $event.target.value)"
    >
        <option v-for="option in options" :key="option.id" :value="option.id">{{option.text}}</option>
    </select>
</template>


<script>
    export default {
        props: ["value", "allowed"],
        data: function () {
            return {
                all_options: [],
            }
        },
        computed: {
            options: function () {

                if (!this.all_options) {
                    return this.all_options;
                }

                if (!this.allowed || this.allowed.length == 0) {
                    return this.all_options
                }

                return this.all_options.filter(o => {
                    return this.allowed.indexOf(o.id) > -1
                })
            },
            disabled: function () {
                const hasZeroOptions = this.options.length === 0;
                const hasOneOption = this.options.length === 1;
                if (hasZeroOptions || (hasOneOption && this.options[0].id === "")) {
                    return true;
                } else {
                    return false;
                }
            }
        },
        beforeMount: function () {
            let options = this.$slots.default
                .filter(node => node.tag == 'option')
                .map(option => {
                    const id = option.data.attrs.value
                    const text = option.children[0].text
                    const selected = option.data.attrs.selected != undefined
                    return {id, text, selected}
                });
            this.all_options = options
        }
    };
</script>

