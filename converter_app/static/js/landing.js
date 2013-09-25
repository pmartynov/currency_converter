(function () {
    function is_valid(input) {
        return input.val().match(/^[0-9]+(\.[0-9]{1,2})?$/);
    }

    $(document).ready(function() {
        var exchanger = $(".exchanger")
        var amount_wrapper = exchanger.find(".amount_wrapper")
        var amount_input = amount_wrapper.find(".amount")
        var convert_btn = exchanger.find(".convert_btn")

        convert_btn.click(function (event) {
            if (!is_valid(amount_input)) {
                amount_wrapper.addClass("error")
                amount_input.one("keypress", function () {
                    amount_wrapper.removeClass("error")
                })

                amount_input.focus()
                event.preventDefault()
            }
            else {
                amount_wrapper.removeClass("error")
            }
        })
    })
})()
