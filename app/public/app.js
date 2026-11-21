function loadHistory() {
  $.getJSON('/api/history', function (rows) {
    var html = '';
    rows.forEach(function (r) {
      html += '<tr><td>' + r.principal + '</td><td>' + r.rate + '</td><td>' + r.months +
              '</td><td>' + r.emi + '</td><td>' + r.servedBy + '</td><td>' +
              new Date(r.createdAt).toLocaleString() + '</td></tr>';
    });
    $('#history').html(html);
  });
}

$('#emiForm').on('submit', function (e) {
  e.preventDefault();                       // no postback
  $('#err').text('');
  var P = parseFloat($('#principal').val());
  var rate = parseFloat($('#rate').val());
  var n = parseInt($('#months').val(), 10);
  if (!(P > 0) || !(rate > 0) || !(n > 0)) {
    $('#err').text('Please enter positive numbers in all fields.');
    return;
  }
  $.ajax({
    url: '/api/emi', method: 'POST', contentType: 'application/json',
    data: JSON.stringify({ principal: P, rate: rate, months: n }),
    success: function (d) {
      $('#rEmi').text(d.emi); $('#rTotal').text(d.totalPayment); $('#rInt').text(d.totalInterest);
      $('#rPod').text(d.servedBy); $('#rIp').text(d.podIp);
      $('#result').show();
      loadHistory();
    },
    error: function (x) { $('#err').text((x.responseJSON && x.responseJSON.error) || 'Request failed'); }
  });
});

loadHistory();
