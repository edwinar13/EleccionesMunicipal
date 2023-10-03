var pdfPath = undefined




$(document).ready(function () {
  $(".link-eje").click(function () {
    $(".link-eje").removeClass("selected-eje");
    $(this).addClass("selected-eje")
  });
});








const datos = {
  1: {
    pdf: 'pdf-genaldo',
    img: 'static/images/photos/foto_genaldo_.png',
    plan: 'plan_1'
  },
  2: {
    pdf: 'pdf-edison',
    img: "static/images/photos/foto_edison_.png",
    plan: 'plan_2'
  },
  3: {
    pdf: 'pdf-blanca',
    img: 'static/images/photos/foto_blanca_lilia_.png',
    plan: 'plan_3'
  },
  4: {
    pdf: 'pdf-mikan',
    img: "static/images/photos/foto_mikan_.png",
    plan: 'plan_4'
  },
  5: {
    pdf: 'pdf-andres',
    img: "static/images/photos/foto_juan_andres_.png",
    plan: 'plan_5'
  }
};



function selectedCandidate(numPlan) {  
  var linkSelected = $("." + datos[numPlan].plan);
  var allSubMenus = $(".link-plan").next("ul");
  allSubMenus.slideUp();
  $(".link-plan").removeClass("selected-plan");

  var subMenu = linkSelected.next("ul");
  subMenu.slideToggle();
  linkSelected.addClass("selected-plan")


  pdfPath =  datos[numPlan].pdf;
  var visorPdfElements = $(".visor-pdf");
  if (pdfPath) {
    visorPdfElements.removeClass("mostrado");
    visorPdfElements.hide();
    var pdfEmbed = $("#" + pdfPath);
    pdfEmbed.addClass("mostrado");
    pdfEmbed.show();
  }

  var imgPath = datos[numPlan].img 
  console.log("omag path"+imgPath)
  if (imgPath) {
    var candidatoImg = $(".candidato-image");
    candidatoImg.attr("src", imgPath);
  }

};

document.addEventListener("DOMContentLoaded", function() {
  var plan = JSON.parse(planValue);
  selectedCandidate(plan)

 
});







function irAPagina(numeroPagina) {
  // Obtener el elemento embed que contiene el PDF
  console.log(pdfPath)
  const pdfEmbed = document.getElementById(pdfPath);
  console.log(pdfEmbed)

  // Verificar si el elemento embed está presente
  if (pdfEmbed) {
    // Cambiar la página actual del PDF utilizando la propiedad "pageNum"
    pdfEmbed.setAttribute('pageNum', numeroPagina);

    // Recargar el PDF para mostrar la página seleccionada
    pdfEmbed.src = pdfEmbed.src;
  }
}