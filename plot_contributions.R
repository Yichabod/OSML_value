library(tidyverse)

df_contributions <- read_csv("2022-02-18 - contributions.csv")

df_repo_weeks <-
  df_contributions %>%
  group_by(repo, date_start) %>%
  summarize(n_users = n()) %>% 
  # fill missing rows as 0 contributions
  group_by(repo) %>%
  mutate(idx=row_number()) %>%
  complete(idx=seq(1,5), fill=list(n_users=0)) %>%
  ungroup()

n_distinct_repos <- unique(df_repo_weeks$repo) %>% length()

n_weekly_active_users <- df_repo_weeks %>% summarize(avg_weekly_users=mean(n_users)) * n_distinct_repos

df_contributions_pytorch <-
  df_contributions %>%
  mutate(lines_add_or_del=lines_add+lines_del) %>%
  filter(github_proj=="pytorch")

df_contributions_tensorflow <-
  df_contributions %>%
  mutate(lines_add_or_del=lines_add+lines_del) %>%
  filter(github_proj=="tensorflow")

colors <- c("All" = "black", "PyTorch" = "red", "Tensorflow" = "blue")

df_contributions %>%
  ggplot(aes(x=commits)) + 
  geom_density(aes(fill='All'), color=NA, alpha=0.5) +
  geom_density(aes(fill='PyTorch'), color=NA, alpha=0.5, data=df_contributions_pytorch) +
  geom_density(aes(fill='Tensorflow'), color=NA, alpha=0.5, data=df_contributions_tensorflow) +  
  scale_fill_manual(values=colors) +
  scale_x_continuous(limits=c(0,50)) +
  labs(title="Distribution of Commits per User-Week") +
  theme_minimal()

df_contributions %>%
  ggplot(aes(x=lines_add)) + 
  geom_density(aes(fill='All'), color=NA, alpha=0.5) +
  geom_density(aes(fill='PyTorch'), color=NA, alpha=0.5, data=df_contributions_pytorch) +
  geom_density(aes(fill='Tensorflow'), color=NA, alpha=0.5, data=df_contributions_tensorflow) +  
  scale_fill_manual(values=colors) +
  labs(title="Distribution of Lines Added per User-Week") +
  #scale_x_continuous(limits=c(0,50)) +
  theme_minimal()

df_contributions %>%
  ggplot(aes(x=lines_del)) + 
  geom_density(aes(fill='All'), color=NA, alpha=0.5) +
  geom_density(aes(fill='PyTorch'), color=NA,alpha=0.5, data=df_contributions_pytorch) +
  geom_density(aes(fill='Tensorflow'), color=NA,alpha=0.5, data=df_contributions_tensorflow) +  
  scale_fill_manual(values=colors) +
  labs(title="Distribution of Lines Deleted per User-Week") +
  scale_x_continuous(limits=c(0,750)) +
  theme_minimal()

df_contributions %>%
  mutate(lines_add_or_del=lines_add+lines_del) %>%
  ggplot(aes(x=lines_add_or_del)) + 
  geom_density(aes(fill='All'), color=NA, alpha=0.5) +
  geom_density(aes(fill='PyTorch'), color=NA,alpha=0.5, data=df_contributions_pytorch) +
  geom_density(aes(fill='Tensorflow'), color=NA,alpha=0.5, data=df_contributions_tensorflow) +  
  scale_fill_manual(values=colors) +
  labs(title="Distribution of Lines Added or Deleted per User-Week") +
  scale_x_continuous(limits=c(0,750)) +
  theme_minimal()


