output "alb_dns_name" {
  description = "Public DNS name of the load balancer (visit http://<dns>/ for the dashboard)"
  value       = aws_lb.main.dns_name
}

output "ecr_repository_url" {
  description = "ECR repository to push the price-service image to"
  value       = aws_ecr_repository.price_service.repository_url
}

output "ecs_cluster_name" {
  description = "ECS cluster running the service"
  value       = aws_ecs_cluster.main.name
}

output "health_check_url" {
  description = "Health endpoint behind the ALB"
  value       = "http://${aws_lb.main.dns_name}/health"
}
