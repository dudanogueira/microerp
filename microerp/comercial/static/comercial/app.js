var ComercialApp = angular.module('ComercialApp', ["ngRoute", "ui.bootstrap", "angular.filter"]);

angular.module("ComercialApp").value("config", {
	baseUrl: "/comercial/api/"
});