angular.module("ComercialApp").factory("ComercialAPI", function ($http, config) {

	var _getPreCliente = function (id) {
		return $http.get(config.baseUrl + "precliente/" + id);
	};
	return {
		getPreCliente: _getPreCliente
	};
});