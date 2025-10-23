

$(document).ready(function () {

  // Voir plus / Voir moins
  const $toggleBtn = $('#toggle-btn');
  const $listWrapper = $('.list-wrapper');
  if ($toggleBtn.length && $listWrapper.length) {
    $toggleBtn.on('click', function () {
      $listWrapper.toggleClass('expanded');
      $toggleBtn.text($listWrapper.hasClass('expanded') ? 'Voir moins' : 'Voir plus');
    });
  }

  // Sélectionner / désélectionner tous les checkboxes
  const $selectAll = $('#select-all');
  const $checkboxes = $('.row-checkbox');

  if ($selectAll.length && $checkboxes.length) {
    $selectAll.on('change', function () {
      const checked = $(this).is(':checked');
      $checkboxes.prop('checked', checked);
    });
  }

  // Soumission du formulaire
  const $form = $('#qr-form');
  const $hiddenInput = $('#selected-ids');

  if ($form.length && $hiddenInput.length) {
    $form.on('submit', function (e) {
      e.preventDefault();
      const selectedIds = $('.row-checkbox:checked').map(function () {
        return $(this).val();
      }).get();

      if (selectedIds.length === 0) {
        alert("Veuillez sélectionner au moins un adhérent.");
        return;
      }

      $hiddenInput.val(selectedIds.join(','));

      // Décommente si tu veux vraiment envoyer
       this.submit();

      // Pour test
      console.log("Soumission avec IDs :", selectedIds);
    });
  }


  // Soumission du formulaire
  const $form2 = $('#qr-form2');
  const $hiddenInput2 = $('#selected-ids2');

  if ($form2.length && $hiddenInput2.length) {
    $form2.on('submit', function (e) {
      e.preventDefault();
      const selectedIds2 = $('.row-checkbox:checked').map(function () {
        return $(this).val();
      }).get();

      if (selectedIds2.length === 0) {
        alert("Veuillez sélectionner au moins un adhérent.");
        return;
      }

      $hiddenInput2.val(selectedIds2.join(','));

      // Décommente si tu veux vraiment envoyer
       this.submit();

      // Pour test
      console.log("Soumission avec IDs :", selectedIds2);
    });
  }

});

