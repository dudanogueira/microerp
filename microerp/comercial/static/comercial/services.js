angular.module("ComercialApp").factory("ComercialAPI", function ($http, config) {

	var _getProposta = function (id) {
		return $http.get(config.baseUrl + "/proposta/" + id);
	};

	return {
		getProposta: _getPropostas,
	};
});