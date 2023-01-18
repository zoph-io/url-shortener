.DEFAULT_GOAL ?= url
.PHONY: url

.PHONY: default
default: help ;

help:
	@echo "Name: ${Product}-${Project}"
	@echo "Description: ${Description}"
	@echo "Credits: zoph.io - https://zoph.io"
	@echo ""
	@echo "Available commands:"
	@echo "	build - build artifacts ${Product} for ${Project}"
	@echo "	deploy - deploy ${Product} for ${Project} - deploy also run 'build' command"
	@echo "	url - create a shorten url using: make url 'https://google.com'"
	@echo "	---"
	@echo "	delete - delete ${Product} for ${Project}"
	@echo "	clean - clean the build folder and artifacts"

###################### Parameters ######################
Product := url-shortener
Project := asd
Environment := dev
Description := ${Product} - ${Project} - ${Environment}

# Shortener Configuration
MinChar := 3
MaxChar := 3

# DNS
Domain := zoph.io
SubDomain := shortener
HostedZoneId := Z1BPJ53MJJG818
FallbackUrl := https://zoph.io

# Certificate (wildcard in us-east-1)
CertificateArn := arn:aws:acm:us-east-1:567589703415:certificate/32d12307-3fd1-4685-9e29-096820fc9d85

# Shortener region
AWSRegion := eu-west-1

# Monitoring
AlertsRecipient := victor@zoph.io
#######################################################

build: clean
	sam build

url:
	@echo '{"long_url": "$(filter-out $@,$(MAKECMDGOALS))"}' | http POST https://${SubDomain}.${Domain}/create

retreive:
	@http https://${SubDomain}.${Domain}/aEe

# used to pass parameters directly with makefile (make url)
%:
	@:

deploy: build
	sam deploy \
		-t .aws-sam/build/template.yaml \
		--region ${AWSRegion} \
		--stack-name "${Project}-${Product}-main-${Environment}" \
		--capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
		--resolve-s3 \
		--force-upload \
		--parameter-overrides \
			pDomain=${Domain} \
			pSubDomain=${SubDomain} \
			pEnv=${Environment} \
			pAWSRegion=${AWSRegion} \
			pMinChar=${MinChar} \
			pMaxChar=${MaxChar} \
			pProjectName=${Project} \
			pProductName=${Product} \
			pDescription='${Description}' \
			pAlertsRecipient='${AlertsRecipient}' \
			pHostedZoneId=${HostedZoneId} \
			pCertificateArn='${CertificateArn}' \
			pFallbackUrl='${FallbackUrl}' \
		--no-fail-on-empty-changeset
	
copy_front:
	@sed -e "s/\__PLACEHOLDER__/${SubDomain}.${Domain}/" ./frontend/js.js > ./frontend/script.js
	@aws s3 cp ./frontend/index.htm s3://short.${Domain}/
	@aws s3 cp ./frontend/styles.css s3://short.${Domain}/
	@aws s3 cp ./frontend/script.js s3://short.${Domain}/
	@aws cloudfront create-invalidation --distribution-id "E3K1HJ8UJ31GZ9" --path "/*"


delete:
	sam delete --stack-name "${Project}-${Product}-main-${Environment}"

clean:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr htmlcov/
	@rm -fr site/
	@rm -fr .eggs/
	@rm -fr .tox/
	@rm -fr .aws-sam/
	@find . -name '*.egg-info' -exec rm -fr {} +
	@find . -name '.DS_Store' -exec rm -fr {} +
	@find . -name '*.egg' -exec rm -f {} +
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
	@find . -name '__pycache__' -exec rm -fr {} +
