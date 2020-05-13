
function currentDateString() {
	const monthNames = ["January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"];
	const d = new Date();
	const dateString = monthNames[d.getMonth()]+" "+d.getDate()+", "+d.getFullYear()
	return dateString
}
