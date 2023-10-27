function enviarRow(mesaId) {
    console.log("Enviando fila " + mesaId);

    // Obtén los valores de los campos de entrada de la fila
    const fila = document.getElementById(`row-${mesaId}`);
    const edison = fila.querySelector("input[name=edison]").value;
    const juan = fila.querySelector("input[name=juan]").value;
    const genaldo = fila.querySelector("input[name=genaldo]").value;
    const mikan = fila.querySelector("input[name=mikan]").value;
    const blanca = fila.querySelector("input[name=blanca]").value;
    const voto_blanco = fila.querySelector("input[name=voto_blanco]").value;
    const nulos = fila.querySelector("input[name=nulos]").value;
    const loading = document.getElementById(`loading-${mesaId}`);
    //agregar clase .loader-on 
    loading.classList.add("loader-on");

    // Envía los datos al servidor utilizando AJAX
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/save_row", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            // Oculta la animación de carga después de recibir la respuesta
            
            //esto se ejecute despues de 2segundos
            setTimeout(function () {
                loading.classList.remove("loader-on");
                loading.style.visibility = "hidden";
            }, 2000);


            if (xhr.status === 200) {
                // Maneja la respuesta del servidor si es necesario
                console.log("Respuesta del servidor: ", xhr.responseText);
            } else {
                // Maneja errores si es necesario
                console.error("Error en la solicitud al servidor.");
            }
        }
    };

    const data = {
        mesaId: mesaId,
        edison: edison,
        juan: juan,
        genaldo: genaldo,
        mikan: mikan,
        blanca: blanca,
        voto_blanco: voto_blanco,
        nulos: nulos
    };

    xhr.send(JSON.stringify(data));
}

$(document).ready(function () {
    $(".edit-input").on("input", function () {

        const parent = $(this).parent();
        const row = parent.parent();
        const mesaId = row.data("mesa-id")
        const loading = $(`#loading-${mesaId}`);

        console.log("Cambio detectado");
        console.log(row);
        console.log(mesaId);

        loading.css("visibility", "visible");
    });
});



const btnReload = document.getElementById("btn-reload");
btnReload.addEventListener("click", function () {
    location.reload();
});


const state = document.getElementById('state');



function checkChangeInformation() {
    $.ajax({
      url: '/check_change_votes', 
      method: 'GET',
      success: function (data) {
        // Comprueba si la información ha cambiado
        console.log('Información actualizada:', data);
        if (data.success) {
          // Agrega una clase al elemento HTML si ha cambiado
          state.classList.add("state-true");
        }
      },
      error: function (error) {
        console.error('Error al verificar cambios:', error);
      }
    });
  }
  

  setInterval(checkChangeInformation, 10000);
  