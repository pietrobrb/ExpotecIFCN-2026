let originalValue = "";
let elements;

$(function(){    
    
    $('.select_user').on("focus", function () {
        originalValue = $(this).val(); 
    });

    $(".select[readonly=readonly]").on('mousedown', function(e) {
        e.preventDefault();
    });
 

    const initializeInputs = (form_id = "form") => {
        elements = document.querySelectorAll(
            form_id + " input[data-maxlength]"
        );

        if (elements.length === 0) {
            elements = document.querySelectorAll(form_id + " input");
        }

        elements.forEach((node) => {
            if(node.getAttribute("data-maxlength")){
                node.setAttribute("maxlength", node.getAttribute("data-maxlength"));
            }
        });

        // Aplica as máscaras de entrada
        elements = document.querySelectorAll(form_id + " input[data-inputmask]");
        Inputmask().mask(elements);

        // Configura as opções padrão do Inputmask
        Inputmask.extendDefaults({
        removeMaskOnSubmit: true,
        });
    };

    initializeInputs();

    $("#app-modal").on("shown.bs.modal", function (event) {
        initializeInputs("#change-form");
    });
    
});
