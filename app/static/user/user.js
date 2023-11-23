function bookingConfirmation(turf_id, turf_date, turf_time){
	$.ajax({
		type: 'POST',
		url: '/bookingConfirmation',
		data: {
			'turf_id' : turf_id,
			'turf_booking_date' : turf_date,
            'turf_booking_time' : turf_time
			},
		success: function(response){
			$('#bokking-confirmation-message').html(response);
            $("#staticBackdrop").modal('show');
		}
	});
}

function confirmBooking(turf_id, turf_date, turf_time){
	$.ajax({
		type: 'POST',
		url: '/confirmUserBooking',
		data: {
			'turf_id' : turf_id,
			'turf_booking_date' : turf_date,
            'turf_booking_time' : turf_time
			},
		success: function(response){
			$('#confirmation-message').html(response);
            $("#staticBackdrop2").modal('show');
		}
	});
}
