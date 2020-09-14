
import 'popper.js'
import 'bootstrap'
import jquery from 'jquery'

// we need this to include the template compiler
import Vue from 'vue/dist/vue.js';

import DashboardTile from './components/dashboard-tile.vue';
import ArcSelect from './components/arc-select.vue';


const $ = jquery

// Trigger a page reload when a user navigates using the back button.
// This code changes default behaviour of the forward button as well.
addEventListener('pageshow', (event) => { if (event.persisted) location.reload(); }) // For Safari
if (performance && performance.navigation && performance.navigation.type === 2) {
    // Other older browsers
    location.reload();
} else if (performance && performance.getEntriesByType) {
    // Other newer browsers
    const perfEntries = performance.getEntriesByType('navigation');

    const perfEntry = perfEntries[0];

    if (perfEntry && perfEntry.type === 'back_forward') {
        location.reload();
    }
}

Vue.component('dashboard-tile', DashboardTile);
Vue.component('arc-select', ArcSelect);

// toasts
$(document).ready(function () {
    $("[data-toast]").toast({delay: 4 * 1000});
    $("[data-toast]").toast('show');
    $('[data-toggle="tooltip"]').tooltip();
});


const arc = {
    utils: {
        load_json_script: (prefix = "data-inject-") => {
            const data = {}
            document.querySelectorAll('[id^=data-inject]').forEach(el => {
                const value = JSON.parse(el.textContent);
                const key = el.id.replace(prefix, "")
                data[key] = value;
            })
            return data;
        }
    },
    page: {
        default: () => {
            new Vue({el: '#vue-app'});
        },
        terms_of_service: () => {
            new Vue({
                el: '#vue-app',
                data: {tos_accepted: false},
            });
        },
        confirm_w_text_form: (mountNode) => {
            new Vue({
                el: mountNode,
                data: {confirmMessage: ''},
                computed: {
                    formValid: function() {
                        return !!this.confirmMessage;
                    }
                },
            });
        },
        reject_request_form: (mountNode) => {
            new Vue({
                el: mountNode,
                data: {statusReason: '', statusReasonSensitive: false},
                computed: {
                    formValid: function() {
                        return !!this.statusReason;
                    }
                },
            });
        },
        validate_attribution_form: (mountNode, {available, attributed, remaining, requestQuantity}) => {
            new Vue({
                    el: mountNode,
                    data: {available, attributed, remaining, requestQuantity},
                    watch: {
                        attributed: function () {
                            this.remaining = this.available - this.attributed < 0 ? 0 : this.available - this.attributed ;
                        }
                    },
                    computed: {
                        hasError: function () {
                            return (this.available - this.attributed < 0 || this.requestQuantity - this.attributed < 0) ? true : false;
                        },
                         isNegative: function () {
                            if (this.attributed < 0)
                                return true;
                        },
                         cannotSave: function () {
                            if (this.attributed < 0)
                                return true;
                            if (this.attributed === '' || this.requestQuantity == 0)
                                return true;
                            return (this.available - this.attributed < 0 || this.requestQuantity - this.attributed < 0) ? true : false;
                        },
                    }
                }
            );
        },
        supply_request_form: ({resource, resourceType, category, item, relations, product_is_missing}) => {

            const _get_from_relations = (relations, resource, resourceType, category, item) => {
                if (!relations[resource]) {
                    return
                }

                const resourcesType = relations[resource];
                if (!resourceType && resourceType !== "") {
                    return resourcesType
                }

                if (!resourcesType[resourceType]) {
                    return
                }

                const categories = resourcesType[resourceType].categories;
                if (!category && category !== "") {
                    return categories
                }

                if (!categories[category]) {
                    return
                }

                const items = categories[category].items

                if (!item) {
                    return items;
                }

                return items[item]

            }


            new Vue({
                el: '#vue-app',
                data: {resource, resourceType, category, item, product_is_missing},
                watch: {
                    resource: function () {
                        this.resourceType = ""
                    },
                    resourceType: function () {
                        this.category = ""
                    },
                    category: function () {
                        this.item = "";
                    }
                },
                computed: {
                    allowed_resourceType: function () {
                        const resourceType = _get_from_relations(relations, this.resource)
                        if (resourceType) {
                            return ["", ...Object.keys(resourceType)]
                        }
                        return [""]
                    },
                    allowed_categories: function () {
                        const categories = _get_from_relations(relations, this.resource, this.resourceType)
                        if (categories) {
                            return ["", ...Object.keys(categories)]
                        }
                        return [""]
                    },
                    allowed_items: function () {
                        const items = _get_from_relations(relations, this.resource, this.resourceType, this.category)
                        if (items) {
                            return ["", ...Object.keys(items)]
                        }
                        return [""]
                    },
                    comment: function () {
                        const item = _get_from_relations(relations, this.resource, this.resourceType, this.category, this.item)
                        if (item) {
                            return item.comment || false
                        }
                        return false
                    }
                }
            });
        },
    }
}

window.arc = arc;
