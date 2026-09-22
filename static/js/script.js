function checkEmpty(selector) {
  if (selector.val()=="" || selector.val()==selector.prop("placeholder")) {
    selector.addClass('formFieldError',500);
    return false;
  } else {
    selector.removeClass('formFieldError',500); 
    return true;
  }
}
function validateEmail(email) {
  var regex = /^[a-zA-Z0-9._-]+@([a-zA-Z0-9.-]+\.)+[a-zA-Z0-9.-]{2,4}$/;
  if (!regex.test(email.val())) {
    email.addClass('formFieldError',500); 
    return false;
  } else {
    email.removeClass('formFieldError',500); 
    return true;
  }
}

jQuery('.contact-form').on('submit', function (e) {
    e.preventDefault();
    var $this = $(this),
		result = true;
	//var response = grecaptcha.getResponse();
	if (!checkEmpty($this.find('#fname'))) {
		result = false;
	}
	if (!checkEmpty($this.find('#lname'))) {
		result = false;
	}
	if (!validateEmail($this.find('#email'))) {
		result = false;
	}
	if (!checkEmpty($this.find('#phoneno'))) {
		result = false;
	}
	if (!checkEmpty($this.find('#messagearea'))) {
		result = false;
	}
	/*if(response.length == 0 && response.length == ''){
	    $('#result-message').addClass('alert alert-danger').html('<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button><strong>Error!</strong> Captch Field Required').delay(500).slideDown(500).delay(10000).slideUp('slow');
	    result = false;
	}else{
	    result = true;
	}*/
	if (result == false) {
		return false;
	}
	else{
    	var data = $(this).serialize(); 
    	$.ajax({
    		url: "/submit_contact",
    		type: "POST",
    		data: data,
    		cache: false,
    		success: function (html) {
    			if (html == 1) {
    				$('#result-message').addClass('alert alert-success').html('<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button><strong>Success!</strong> Message Send. We will contact with you soon.').delay(500).slideDown(500).delay(10000).slideUp('slow');
    			} else {
    				$('#result-message').addClass('alert alert-danger').html('<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button><strong>Error!</strong> Message Sending Error! Please try again').delay(500).slideDown(500).delay(10000).slideUp('slow');
    			}
    			$('#contactform').find("input[type=text],input[type=email], textarea").val("");
    			//grecaptcha.reset();
    		},
    		error: function (a, b) {
    			if (b == 'error') {
    				$('#result-message').addClass('alert alert-danger').html('<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">×</span></button><strong>Error!</strong> Message Sending Error! Please try again').delay(500).slideDown(500).delay(10000).slideUp('slow');
    			};
    			//grecaptcha.reset();
    		}
    	});
    	return false;
    }
});