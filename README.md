# Serverless url-shortener

## 🧠 Rational

This AWS serverless url-shortener is used for [AWS Security Digest Newsletter](https://asd.zoph.io) to shorten urls and also act as simple hits counter for analytics purpose. It could make sense for you too, so feel free to deploy it for your own usage. PR accepted.

## 💡 Features

1. urls shortener
   1. API (`Create`)
   2. Static website
2. hits counter

## 🚀 Usage

### Pre-requirements

1. You will need to have an already issued wilcard ACM Certificate in `us-east-1` AWS region: `*.{your_domain}`
2. Set the proper parameters in the `Makefile`

#### Parameters

| Parameter       | Default Value   | Description                                                   |
| --------------- | --------------- | ------------------------------------------------------------- |
| Product         | url-shortener   | Product Name                                                  |
| Project         | asd             | Project Name                                                  |
| Environment     | dev             | Environment Name                                              |
| MinChar         | 3               | Minimum characters for the random shortened link id           |
| MaxChar         | 3               | Maximum characters for the random shortened link id           |
| Domain          | zoph.io         | Desired Domain (must be linked to the HostedZoneId Parameter) |
| SubDomain       | shortener       | Desired subdomain of the api                                  |
| HostedZoneId    | `Required`      | Route53 HostedZoneId where your domain belongs                |
| FallbackUrl     | https://zoph.io | When the url does not exist, fallback url                     |
| CertificateArn  | `Required`      | Arn of the Wildcard ACM Certificate (`us-east-1`)             |
| AWSRegion       | eu-west-1       | AWS Region of the Shortener                                   |
| AlertsRecipient | `Required`      | Email of the recipient of CloudWatch Alarms                   |

### Deployment

        $ make deploy

### Shorten urls

### Using Static Website

Go to the following website after the deployment.

- [https://short.{domain}]()

#### Using `Makefile`

        $ make url 'https://google.com'

#### Using `cURL`

```bash
curl -X POST https://{subdomain}.{domain}/create/ \
     --header "Content-Type: application/json" \
     -d '{"long_url": "https://google.com"}'
```

## 📖 Reference

- [Blog post](https://blog.ruanbekker.com/blog/2018/11/30/how-to-setup-a-serverless-url-shortener-with-api-gateway-lambda-and-dynamodb-on-aws/)
- [Makefile](https://itecnote.com/tecnote/r-how-to-pass-argument-to-makefile-from-command-line/)
- [CloudFront Stack](https://github.com/aws-samples/amazon-cloudfront-secure-static-site/tree/master)

## Todo

1. Cleanup Makefile and Readme
2. Handle CSP
3. Handle CORS Properly
4. Re-Deploy from Scratch - Multiple-times
5. Estimate deployment time
6. Add destription to CloudFront Distribution
7. Tags everywhere
